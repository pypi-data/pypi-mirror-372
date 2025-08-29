import copy
import json
import logging
import os
import shutil

from collections import OrderedDict
from pathlib import Path

import trimesh

from lxml import etree as ET
from manipulation.make_drake_compatible_model import MakeDrakeCompatibleModel
from tqdm import tqdm

from mesh_to_sim_asset.mesh_conversion import (
    convert_blend_to_gltf,
    convert_dae_to_gltf,
    convert_fbx_to_gltf,
    convert_glb_to_gltf,
    convert_glb_to_obj,
    convert_obj_to_gltf,
    convert_ply_to_gltf,
)
from mesh_to_sim_asset.mesh_simplification import (
    run_rolopoly,
    simplify_mesh_non_destructive,
)
from mesh_to_sim_asset.mesh_to_vtk import convert_mesh_to_vtk
from mesh_to_sim_asset.physics import (
    compute_hydroelastic_modulus,
    get_composed_asset_physics_properties,
)
from mesh_to_sim_asset.sdformat import (
    add_compliant_proximity_properties_element,
    add_convex_decomposition_collision_element_with_proximity_properties,
    add_inertial_properties_element_multiple_meshes,
    add_mesh_element,
    format_xml_for_pretty_print,
)
from mesh_to_sim_asset.usd_to_sdf import convert_usd_to_sdf_usd2sdf, parse_sdf_file
from mesh_to_sim_asset.util import (
    CollisionGeomType,
    OpenAIModelType,
    get_basename_without_extension,
    get_metadata_if_exists,
)

# Set up logger.
logger = logging.getLogger(__name__)


def should_skip_existing(
    asset_path: Path, output_dir: Path, collision_geom_types: list[CollisionGeomType]
) -> bool:
    """Check if we should skip processing this asset because output already exists.

    Args:
        asset_path: Path to the input asset file.
        output_dir: Output directory.
        collision_geom_types: List of collision geometry types.

    Returns:
        True if should skip, False otherwise.
    """
    asset_name = get_basename_without_extension(asset_path)
    asset_output_dir = output_dir / asset_name

    if not asset_output_dir.exists():
        return False

    # Check if the main SDF file exists.
    main_sdf_path = asset_output_dir / f"{asset_name}.sdf"
    if main_sdf_path.exists():
        return True

    # Check if collision-specific SDF files exist.
    for geom_type in collision_geom_types:
        if geom_type == CollisionGeomType.CoACD:
            sdf_path = asset_output_dir / f"{asset_name}_coacd.sdf"
        elif geom_type == CollisionGeomType.VHACD:
            sdf_path = asset_output_dir / f"{asset_name}_vhacd.sdf"
        elif geom_type == CollisionGeomType.VTK:
            sdf_path = asset_output_dir / f"{asset_name}_vtk.sdf"
        else:
            continue

        if sdf_path.exists():
            return True

    return False


def convert_asset_to_drake_sdf(asset_path: Path) -> Path:
    """Convert an asset file to a Drake-compatible SDF file with enhanced USD support.

    This function uses sophisticated USD processing that preserves textures
    and materials through GLTF export, providing better visual quality.

    Args:
        asset_path: The path to the asset file.

    Returns:
        The path to the SDF file.

    Raises:
        ValueError: If the asset file type is not supported.
    """
    # Check if the asset exists.
    if not asset_path.exists():
        raise FileNotFoundError(f"Asset file not found: {asset_path}")

    # Check if the asset is a file.
    if not asset_path.is_file():
        raise FileNotFoundError(f"Asset file not found: {asset_path}")

    output_path = asset_path.with_suffix(".sdf")

    if asset_path.suffix.lower() in [".usd", ".usda", ".usdc"]:
        # Use the sophisticated USD to SDF conversion that preserves materials
        # and textures through GLTF export.
        convert_usd_to_sdf_usd2sdf(usd_path=asset_path, sdf_path=output_path)

    elif asset_path.suffix.lower() in [".urdf", ".sdf", ".xml"]:
        # Make Drake-compatible for URDF/SDF files.
        MakeDrakeCompatibleModel(
            input_filename=asset_path.as_posix(),
            output_filename=output_path.as_posix(),
            overwrite=True,
        )

    else:
        raise ValueError(f"Unsupported asset file type: {asset_path}")

    return output_path


def extract_mesh_paths_from_sdf(
    sdf_path: Path, visual_elements: list[ET.Element]
) -> tuple[OrderedDict[str, list[Path]], OrderedDict[str, list[Path]]]:
    """Extract mesh paths from SDF visual elements and convert to required formats.

    Args:
        sdf_path: Path to the SDF file.
        visual_elements: List of visual XML elements.

    Returns:
        Tuple of (link_name_to_gltf_paths, link_name_to_obj_paths).

    Raises:
        NotImplementedError: If primitive geometries are encountered.
        ValueError: If unsupported mesh file format is found.
    """
    link_name_to_gltf_paths: OrderedDict[str, list[Path]] = OrderedDict()
    link_name_to_obj_paths: OrderedDict[str, list[Path]] = OrderedDict()

    for visual in visual_elements:
        for geometry in visual.xpath(".//geometry"):
            # Get the actual geometry type (child of geometry element).
            geometry_type_elements = geometry.getchildren()
            if not geometry_type_elements:
                continue

            geometry_type = geometry_type_elements[
                0
            ]  # Should be mesh, box, cylinder, or sphere

            if geometry_type.tag in ["box", "cylinder", "sphere"]:
                raise NotImplementedError(
                    "Primitive geometries are not supported yet for physics estimation, etc."
                )

            elif geometry_type.tag == "mesh":
                mesh_path = os.path.join(
                    sdf_path.parent, geometry_type.find("uri").text
                )
                mesh_path = Path(mesh_path).resolve()

                # Convert the input mesh to a GLTF mesh.
                gltf_path = mesh_path.with_suffix(".gltf")
                mesh_suffix_lower = mesh_path.suffix.lower()
                if mesh_suffix_lower == ".obj":
                    convert_obj_to_gltf(mesh_path, gltf_path)
                elif mesh_suffix_lower == ".ply":
                    convert_ply_to_gltf(mesh_path, gltf_path)
                elif mesh_suffix_lower == ".fbx":
                    convert_fbx_to_gltf(mesh_path, gltf_path)
                elif mesh_suffix_lower == ".blend":
                    convert_blend_to_gltf(mesh_path, gltf_path)
                elif mesh_suffix_lower == ".dae":
                    convert_dae_to_gltf(mesh_path, gltf_path)
                elif mesh_suffix_lower == ".gltf":
                    # This conversion ensures that we end up with a gltf file with
                    # separate texture files as desired by Drake.
                    convert_glb_to_gltf(mesh_path, gltf_path)
                elif mesh_suffix_lower == ".glb":
                    convert_glb_to_gltf(mesh_path, gltf_path)
                else:
                    raise ValueError(f"Unsupported mesh file: {mesh_path}")

                # Make the GLTF path relative to the SDF file for portability.
                gltf_path_relative = gltf_path.relative_to(sdf_path.parent)
                geometry_type.find("uri").text = gltf_path_relative.as_posix()

                link_name = visual.getparent().get("name")
                link_name_to_gltf_paths.setdefault(link_name, [])
                link_name_to_gltf_paths[link_name].append(gltf_path)

                # Create an OBJ version for the collision mesh.
                mesh_path_obj = mesh_path.parent / f"{mesh_path.stem}.obj"
                convert_glb_to_obj(mesh_path, mesh_path_obj)
                link_name_to_obj_paths.setdefault(link_name, [])
                link_name_to_obj_paths[link_name].append(mesh_path_obj)

    return link_name_to_gltf_paths, link_name_to_obj_paths


def get_physics_properties_for_links(
    sdf_path: Path,
    link_name_to_gltf_paths: OrderedDict[str, list[Path]],
    keep_images: bool,
    use_cpu_rendering: bool,
    model_type: OpenAIModelType,
) -> tuple[dict, OrderedDict[str, dict]]:
    """Get physics properties for all links in the asset.

    Args:
        sdf_path: Path to the SDF file.
        link_name_to_gltf_paths: Mapping from link names to GLTF paths.
        keep_images: Whether to keep rendered images.
        use_cpu_rendering: Whether to use CPU rendering.
        model_type: OpenAI model type to use.

    Returns:
        Tuple of (overall_physics_props, link_name_to_physics_props).
    """
    # Get the physical properties for each geometry.
    images_path = sdf_path.parent / "mesh_renders" if keep_images else None
    metadata = get_metadata_if_exists(mesh_path=sdf_path)
    gltf_paths = [p for paths in link_name_to_gltf_paths.values() for p in paths]
    physics_props = get_composed_asset_physics_properties(
        gltf_paths=gltf_paths,
        images_path=images_path,
        use_cpu_rendering=use_cpu_rendering,
        metadata=metadata,
        model=model_type.get_model_id(),
    )

    # Create a mapping from link name to physics properties.
    link_name_to_physics_props: OrderedDict[str, dict] = OrderedDict()
    subparts_index = 0
    for link_name, mesh_paths in link_name_to_gltf_paths.items():
        num_meshes = len(mesh_paths)
        link_physics_props = physics_props["subparts"][
            subparts_index : subparts_index + num_meshes
        ]
        link_name_to_physics_props[link_name] = link_physics_props
        subparts_index += num_meshes

    # Save the physics properties to a json file.
    physics_props_path = sdf_path.parent / f"{sdf_path.stem}_properties.json"
    with open(physics_props_path, "w", encoding="utf-8") as f:
        json.dump(physics_props, f, indent=2)

    return physics_props, link_name_to_physics_props


def add_inertial_properties_to_links(
    link_elements: list[ET.Element],
    link_name_to_physics_props: OrderedDict[str, dict],
    link_name_to_obj_paths: OrderedDict[str, list[Path]],
) -> None:
    """Add inertial properties to all link elements.

    Args:
        link_elements: List of link XML elements.
        link_name_to_physics_props: Mapping from link names to physics properties.
        link_name_to_obj_paths: Mapping from link names to OBJ mesh paths.
    """
    for link_element, physics_props in zip(
        link_elements, link_name_to_physics_props.values()
    ):
        link_name = link_element.get("name")
        mesh_paths = link_name_to_obj_paths[link_name]

        meshes = [trimesh.load_mesh(p) for p in mesh_paths]
        masses = [p["mass"] for p in physics_props]

        # Compute and add the inertial properties.
        add_inertial_properties_element_multiple_meshes(
            masses=masses, meshes=meshes, link_item=link_element
        )


def add_coacd_collision_geometries(
    link_elements: list[ET.Element],
    link_name_to_physics_props: OrderedDict[str, dict],
    link_name_to_obj_paths: OrderedDict[str, list[Path]],
    output_sdf_path: Path,
    resolution_values: list[float] | None = None,
    volume_change_threshold: float = 0.01,
) -> None:
    """Add CoACD collision geometries to all links.

    Args:
        link_elements: List of link XML elements.
        link_name_to_physics_props: Mapping from link names to physics properties.
        link_name_to_obj_paths: Mapping from link names to OBJ mesh paths.
        output_sdf_path: Path to the output SDF file.
        resolution_values: List of resolution values to try for CoACD iterative
            refinement. If None, uses single-pass behavior.
        volume_change_threshold: Maximum absolute volume improvement (m³)
            per additional part to continue refinement. Default is 0.001 m³.
    """
    for link_element, physics_props in zip(
        link_elements, link_name_to_physics_props.values()
    ):
        link_name = link_element.get("name")
        mesh_paths = link_name_to_obj_paths[link_name]

        for mesh_path, physics_prop in zip(mesh_paths, physics_props, strict=True):
            collision_mesh = trimesh.load_mesh(mesh_path)
            logger.info(f"Adding CoACD collision geometry for {mesh_path}")
            add_convex_decomposition_collision_element_with_proximity_properties(
                link_item=link_element,
                collision_mesh=collision_mesh,
                mesh_parts_dir_name=f"{mesh_path.stem}_coacd",
                output_path=output_sdf_path,
                material_modulus=physics_prop["material_modulus"],
                use_coacd=True,
                coacd_kwargs=None,
                vhacd_kwargs=None,
                hunt_crossley_dissipation=physics_prop.get("hunt_crossley_dissipation"),
                mu_dynamic=physics_prop["mu_dynamic"],
                mu_static=physics_prop["mu_static"],
                collision_name_prefix=f"{mesh_path.stem}_",
                resolution_values=resolution_values,
                volume_change_threshold=volume_change_threshold,
            )
            logger.info(f"Added CoACD collision geometry for {mesh_path}")


def add_vhacd_collision_geometries(
    link_elements: list[ET.Element],
    link_name_to_physics_props: OrderedDict[str, dict],
    link_name_to_obj_paths: OrderedDict[str, list[Path]],
    output_sdf_path: Path,
    resolution_values: list[float] | None = None,
    volume_change_threshold: float = 0.01,
) -> None:
    """Add VHACD collision geometries to all links.

    Args:
        link_elements: List of link XML elements.
        link_name_to_physics_props: Mapping from link names to physics properties.
        link_name_to_obj_paths: Mapping from link names to OBJ mesh paths.
        output_sdf_path: Path to the output SDF file.
        resolution_values: List of resolution values to try for CoACD iterative
            refinement. If None, uses single-pass behavior.
        volume_change_threshold: Maximum absolute volume improvement (m³)
            per additional part to continue refinement. Default is 0.001 m³.
    """
    for link_element, physics_props in zip(
        link_elements, link_name_to_physics_props.values()
    ):
        link_name = link_element.get("name")
        mesh_paths = link_name_to_obj_paths[link_name]

        for mesh_path, physics_prop in zip(mesh_paths, physics_props, strict=True):
            collision_mesh = trimesh.load_mesh(mesh_path)
            logger.info(f"Adding VHACD collision geometry for {mesh_path}")
            add_convex_decomposition_collision_element_with_proximity_properties(
                link_item=link_element,
                collision_mesh=collision_mesh,
                mesh_parts_dir_name=f"{mesh_path.stem}_vhacd",
                output_path=output_sdf_path,
                material_modulus=physics_prop["material_modulus"],
                use_coacd=False,
                coacd_kwargs=None,
                vhacd_kwargs=None,
                hunt_crossley_dissipation=physics_prop.get("hunt_crossley_dissipation"),
                mu_dynamic=physics_prop["mu_dynamic"],
                mu_static=physics_prop["mu_static"],
                collision_name_prefix=f"{mesh_path.stem}_",
                resolution_values=resolution_values,
                volume_change_threshold=volume_change_threshold,
            )
            logger.info(f"Added VHACD collision geometry for {mesh_path}")


def add_vtk_collision_geometries(
    link_elements: list[ET.Element],
    link_name_to_physics_props: OrderedDict[str, dict],
    link_name_to_obj_paths: OrderedDict[str, list[Path]],
    output_sdf_path: Path,
    rolopoly_timeout: int,
) -> bool:
    """Add VTK collision geometries to all links.

    Args:
        link_elements: List of link XML elements.
        link_name_to_physics_props: Mapping from link names to physics properties.
        link_name_to_obj_paths: Mapping from link names to OBJ mesh paths.
        output_sdf_path: Path to the output SDF file.
        rolopoly_timeout: Timeout for RoLoPoly simplification.

    Returns:
        True if all VTK conversions were successful, False otherwise.
    """
    all_conversions_successful = True

    for link_element, physics_props in zip(
        link_elements, link_name_to_physics_props.values()
    ):
        link_name = link_element.get("name")
        mesh_paths = link_name_to_obj_paths[link_name]

        for mesh_path, physics_prop in zip(mesh_paths, physics_props, strict=True):
            # Create a mesh copy for simplification.
            mesh_path_rolopoly = mesh_path.parent / f"{mesh_path.stem}_rolopoly.obj"
            shutil.copy(mesh_path, mesh_path_rolopoly)

            # Use a finer simplification for big meshes with thin parts (e.g., a
            # table with thin legs).
            is_big_with_thin_parts = physics_prop["big_with_thin_parts"]
            screen_size = 250 if is_big_with_thin_parts else 100

            # Clean up the mesh non-destructively before RoLoPoly simplification.
            try:
                logger.info(f"Cleaning up mesh {mesh_path.stem} before RoLoPoly")
                simplify_mesh_non_destructive(mesh_path_rolopoly, mesh_path_rolopoly)
                logger.info(f"Mesh cleanup completed for {mesh_path.stem}")
            except Exception as e:
                logger.warning(
                    f"Mesh cleanup failed for {mesh_path.stem}: {e}. Proceeding with original mesh."
                )

            # Sequentially simplify with RoLoPoly until Tetgen succeeds.
            vtk_path = None
            for i in tqdm(
                range(5),
                desc=f"  Simplifying with RoLoPoly ({mesh_path.stem})",
                leave=False,
                position=1,
            ):
                try:
                    # Simplify with RoLoPoly.
                    output_folder = mesh_path.parent / f"{mesh_path.stem}_rolopoly"
                    logger.info(f"Running RoLoPoly for {mesh_path.stem}")
                    run_rolopoly(
                        input_path=mesh_path_rolopoly,
                        output_folder=output_folder,
                        timeout=rolopoly_timeout,
                        screen_size=screen_size,
                    )
                    logger.info(f"RoLoPoly completed for {mesh_path.stem}")

                    # Replace mesh with the simplified version and clean up.
                    new_mesh_path = (
                        output_folder / f"{mesh_path.stem}_rolopoly_ours_final.obj"
                    )
                    shutil.copy(new_mesh_path, mesh_path_rolopoly)
                    shutil.rmtree(output_folder)

                    logger.info(f"Converting to VTK for {mesh_path.stem}")
                    vtk_path = convert_mesh_to_vtk(input_path=mesh_path_rolopoly)
                    logger.info(f"VTK conversion completed for {mesh_path.stem}")
                    break
                except Exception as e:
                    logger.error(
                        f"Failed to convert {mesh_path.stem} to vtk on iteration "
                        f"{i+1}: {e}"
                    )

                    if "RoLoPoly timed out" in str(e):
                        # No point to try again if failed due to timeout.
                        break
                    continue

            if vtk_path is not None:
                # Compute hydroelastic modulus.
                hydroelastic_modulus = compute_hydroelastic_modulus(
                    material_modulus=physics_prop["material_modulus"],
                    vtk_file_path=vtk_path,
                )

                if is_big_with_thin_parts:
                    # Scale the modulus to prevent penetration at the thin parts.
                    hydroelastic_modulus *= 1e2

                # Make the VTK path relative to the SDF file for portability.
                vtk_path_relative = vtk_path.relative_to(output_sdf_path.parent)
                collision_item = add_mesh_element(
                    mesh_path=vtk_path_relative,
                    link_item=link_element,
                    is_collision=True,
                    name_prefix=f"{mesh_path.stem}_",
                )
                add_compliant_proximity_properties_element(
                    collision_item=collision_item,
                    hydroelastic_modulus=hydroelastic_modulus,
                    hunt_crossley_dissipation=physics_prop.get(
                        "hunt_crossley_dissipation"
                    ),
                    mu_dynamic=physics_prop["mu_dynamic"],
                    mu_static=physics_prop["mu_static"],
                )
            else:
                logger.warning(
                    f"Failed to convert {mesh_path.stem} to vtk after 5 iterations."
                )
                all_conversions_successful = False

    return all_conversions_successful


def make_sdf_geometries_simulatable(
    sdf_path: Path,
    keep_images: bool,
    use_cpu_rendering: bool,
    collision_geom_type: list[CollisionGeomType],
    rolopoly_timeout: int,
    model_type: OpenAIModelType,
    resolution_values: list[float] | None = None,
    volume_change_threshold: float = 0.01,
) -> list[Path]:
    """Make the SDF geometries simulation-ready.

    Args:
        sdf_path: Path to the SDF file.
        keep_images: Whether to keep rendered images.
        use_cpu_rendering: Whether to use CPU rendering.
        collision_geom_type: List of collision geometry types to generate.
        rolopoly_timeout: Timeout for RoLoPoly mesh simplification.
        model_type: OpenAI model type to use for physics analysis.
        resolution_values: List of resolution values to try for CoACD iterative
            refinement. If None, uses single-pass behavior.
        volume_change_threshold: Maximum absolute volume improvement (m³)
            per additional part to continue refinement. Default is 0.001 m³.

    Returns:
        List of output SDF file paths.
    """
    root = parse_sdf_file(sdf_path)

    # Remove all collision elements.
    for collision in root.xpath(".//collision"):
        collision.getparent().remove(collision)

    # Remove all inertial elements (can't trust them).
    for inertial in root.xpath(".//inertial"):
        inertial.getparent().remove(inertial)

    # Get all visual elements and link elements.
    visual_elements: list[ET.Element] = root.xpath(".//visual")
    link_elements: list[ET.Element] = root.xpath(".//link")

    # Extract and convert mesh paths.
    link_name_to_gltf_paths, link_name_to_obj_paths = extract_mesh_paths_from_sdf(
        sdf_path=sdf_path, visual_elements=visual_elements
    )

    # Get physics properties for all links.
    _, link_name_to_physics_props = get_physics_properties_for_links(
        sdf_path=sdf_path,
        link_name_to_gltf_paths=link_name_to_gltf_paths,
        keep_images=keep_images,
        use_cpu_rendering=use_cpu_rendering,
        model_type=model_type,
    )

    # Add inertial properties to all links.
    add_inertial_properties_to_links(
        link_elements=link_elements,
        link_name_to_physics_props=link_name_to_physics_props,
        link_name_to_obj_paths=link_name_to_obj_paths,
    )

    # Create separate SDF files for each collision geometry type.
    multiple_collision_geoms = len(collision_geom_type) > 1
    output_sdf_paths: list[Path] = []

    for geom_type in collision_geom_type:
        # Create a deep copy of the root tree for this collision geometry type.
        root_copy = copy.deepcopy(root)

        # Get the link elements from the copied tree.
        link_elements_copy: list[ET.Element] = root_copy.xpath(".//link")

        # Determine output file name.
        if multiple_collision_geoms:
            if geom_type == CollisionGeomType.CoACD:
                output_sdf_path = sdf_path.parent / f"{sdf_path.stem}_coacd.sdf"
            elif geom_type == CollisionGeomType.VHACD:
                output_sdf_path = sdf_path.parent / f"{sdf_path.stem}_vhacd.sdf"
            elif geom_type == CollisionGeomType.VTK:
                output_sdf_path = sdf_path.parent / f"{sdf_path.stem}_vtk.sdf"
        else:
            # Single collision geometry type, use the original name.
            output_sdf_path = sdf_path

        # Update the model name to match the output SDF file base name.
        model_elements = root_copy.xpath(".//model")
        if model_elements:
            model_elements[0].set("name", output_sdf_path.stem)

        # Add collision geometries based on the specified type.
        if geom_type == CollisionGeomType.CoACD:
            add_coacd_collision_geometries(
                link_elements=link_elements_copy,
                link_name_to_physics_props=link_name_to_physics_props,
                link_name_to_obj_paths=link_name_to_obj_paths,
                output_sdf_path=output_sdf_path,
                resolution_values=resolution_values,
                volume_change_threshold=volume_change_threshold,
            )

        elif geom_type == CollisionGeomType.VHACD:
            add_vhacd_collision_geometries(
                link_elements=link_elements_copy,
                link_name_to_physics_props=link_name_to_physics_props,
                link_name_to_obj_paths=link_name_to_obj_paths,
                output_sdf_path=output_sdf_path,
                resolution_values=resolution_values,
                volume_change_threshold=volume_change_threshold,
            )

        elif geom_type == CollisionGeomType.VTK:
            all_vtk_conversions_successful = add_vtk_collision_geometries(
                link_elements=link_elements_copy,
                link_name_to_physics_props=link_name_to_physics_props,
                link_name_to_obj_paths=link_name_to_obj_paths,
                output_sdf_path=output_sdf_path,
                rolopoly_timeout=rolopoly_timeout,
            )
            if not all_vtk_conversions_successful:
                logger.warning(
                    f"Skipping VTK SDF file creation for {output_sdf_path.name} "
                    f"because not all meshes could be converted to VTK format."
                )
                continue  # Skip writing this SDF file

        # Write the SDF file for this collision geometry type.
        format_xml_for_pretty_print(root_copy)
        ET.ElementTree(root_copy).write(
            output_sdf_path, pretty_print=True, encoding="utf-8"
        )
        output_sdf_paths.append(output_sdf_path)

        logger.info(
            f"Created SDF file with {geom_type.value} collision geometry: "
            f"{output_sdf_path}"
        )

    return output_sdf_paths


def copy_generated_outputs_to_target_dir(
    original_dir: Path, asset_output_dir: Path, simulatable_sdf_paths: list[Path]
) -> list[Path]:
    """Copy generated output files from original directory to target directory.

    Args:
        original_dir: Original directory where processing occurred.
        asset_output_dir: Target output directory.
        simulatable_sdf_paths: List of generated SDF file paths.

    Returns:
        List of copied SDF file paths in the target directory.
    """
    # Copy generated SDF files to the target directory.
    copied_sdf_paths = []
    for generated_sdf_path in simulatable_sdf_paths:
        target_sdf_path = asset_output_dir / generated_sdf_path.name
        shutil.copy2(generated_sdf_path, target_sdf_path)
        copied_sdf_paths.append(target_sdf_path)

    # Copy related output files (collision meshes, converted meshes, properties).
    for item in original_dir.iterdir():
        if item.is_file():
            # Copy generated files: GLTF/OBJ meshes, VTK files, JSON properties.
            if (
                item.suffix.lower() in [".gltf", ".obj", ".vtk", ".bin"]
                or item.name.endswith("_properties.json")
                or item.name.endswith("_rolopoly.obj")
            ):
                shutil.copy2(item, asset_output_dir)
        elif item.is_dir():
            # Copy collision mesh directories (coacd, vhacd directories).
            if (
                "_coacd" in item.name
                or "_vhacd" in item.name
                or "mesh_renders" in item.name
            ):
                target_dir = asset_output_dir / item.name
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(item, target_dir)
            # Copy mesh directories that contain GLTF, OBJ, or other mesh files.
            elif "mesh" in item.name.lower() or any(
                f.suffix.lower() in [".gltf", ".obj", ".glb", ".bin"]
                for f in item.rglob("*")
            ):
                target_dir = asset_output_dir / item.name
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.copytree(item, target_dir)

    return copied_sdf_paths
