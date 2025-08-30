from dataclasses import fields, is_dataclass
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image, PngImagePlugin, ExifTags
import numpy as np
from gradio import image_utils
from gradio_propertysheet.helpers import build_path_to_metadata_key_map

def infer_type(s: str):
    """
    Infers and converts a string to the most likely data type.

    It attempts conversions in the following order:
    1. Integer
    2. Float
    3. Boolean (case-insensitive 'true' or 'false')
    If all conversions fail, it returns the original string.

    Args:
        s: The input string to be converted.

    Returns:
        The converted value (int, float, bool) or the original string.
    """
    if not isinstance(s, str):
        # If the input is not a string, return it as is.
        return s

    # 1. Try to convert to an integer
    try:
        return int(s)
    except ValueError:
        # Not an integer, continue...
        pass

    # 2. Try to convert to a float
    try:
        return float(s)
    except ValueError:
        # Not a float, continue...
        pass
    
    # 3. Check for a boolean value
    # This explicit check is important because bool('False') evaluates to True.
    s_lower = s.lower()
    if s_lower == 'true':
        return True
    if s_lower == 'false':
        return False
        
    # 4. If nothing else worked, return the original string
    return s


def extract_metadata(image_data: str | Path | Image.Image | np.ndarray | None, only_custom_metadata: bool = True) -> Dict[str, Any]:
    """
    Extracts metadata from an image.

    Args:
        image_data: Image data as a filepath, Path, PIL Image, NumPy array, or None.
        only_custom_metadata: If True, excludes technical metadata (e.g., ImageWidth, ImageHeight). Defaults to True.

    Returns:
        Dictionary of extracted metadata. Returns empty dictionary if no metadata is available or extraction fails.
    """
    if not image_data:
        return {}

    try:
        # Convert image_data to PIL.Image
        if isinstance(image_data, (str, Path)):
            image = Image.open(image_data)
        elif isinstance(image_data, np.ndarray):
            image = Image.fromarray(image_data)
        elif isinstance(image_data, Image.Image):
            image = image_data
        elif hasattr(image_data, 'path'):  # For ImageMetaData
            image = Image.open(image_data.path)
        else:
            return {}

        decoded_meta = {}
        if image.format == "PNG":
            if not only_custom_metadata:
                decoded_meta["ImageWidth"] = image.width
                decoded_meta["ImageHeight"] = image.height
            metadata = image.info
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, bytes):
                        value = value.decode(errors='ignore')
                    decoded_meta[str(key)] = value
        else:
            exif_data = image.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        value = value.decode(errors='ignore')
                    decoded_meta[str(tag)] = value
            if not only_custom_metadata:
                decoded_meta["ImageWidth"] = image.width
                decoded_meta["ImageHeight"] = image.height

        return decoded_meta
    except Exception:
        return {}

def preprocess_image(image_data: str | Path | Image.Image | np.ndarray, type: str = "numpy") -> np.ndarray | Image.Image:
    """
    Processes an image to the specified format.

    Args:
        image_data: Image data as a filepath, Path, PIL Image, or NumPy array.
        type: Output format, either "numpy" (array with shape (height, width, 3)) or "pil" (PIL Image). Defaults to "numpy".

    Returns:
        Processed image as a NumPy array or PIL Image.

    Raises:
        ValueError: If image_data type or output type is unsupported.
    """
    if isinstance(image_data, (str, Path)):
        payload = image_data
    elif isinstance(image_data, Image.Image):
        payload = image_data
    elif isinstance(image_data, np.ndarray):
        payload = image_data
    elif hasattr(image_data, 'path'):  # For ImageMetaData
        payload = image_data.path
    else:
        raise ValueError(f"Unsupported image_data type: {type(image_data)}")

    if type == "numpy":
        return image_utils.preprocess_image(payload, type="numpy")
    elif type == "pil":
        return image_utils.preprocess_image(payload, type="pil")
    else:
        raise ValueError(f"Unsupported type: {type}")

def add_metadata(image_data: str | Path | Image.Image | np.ndarray, save_path: str, metadata: Dict[str, Any]) -> bool:
    """
    Adds metadata to an image and saves it to the specified path.

    Args:
        image_data: Image data as a filepath, Path, PIL Image, or NumPy array.
        save_path: Filepath where the modified image will be saved.
        metadata: Dictionary of metadata to add to the image.

    Returns:
        True if metadata was added and image was saved successfully, False otherwise.
    """
    try:
        if not bool(save_path):
            return False        
        
        # Convert image_data to PIL.Image
        if isinstance(image_data, (str, Path)):
            image = Image.open(image_data)
        elif isinstance(image_data, np.ndarray):
            image = Image.fromarray(image_data)
        elif isinstance(image_data, Image.Image):
            image = image_data
        elif hasattr(image_data, 'path'):  # For ImageMetaData
            image = Image.open(image_data.path)
        else:
            return False

        _, ext = os.path.splitext(save_path)
        image_copy = image.copy()
        
        if (image.format if image.format is not None else ext.replace('.','').upper()) == "PNG":
            meta = None
            if metadata:
                meta = PngImagePlugin.PngInfo()
                for key, value in metadata.items():
                    meta.add_text(str(key), str(value))
                image_copy.info.update(metadata)  # For reference, but requires pnginfo when saving
            image_copy.save(save_path, pnginfo=meta)
        else:
            if metadata:
                exif = image_copy.getexif() or Image.Exif()
                for key, value in metadata.items():
                    tag_id = next((k for k, v in ExifTags.TAGS.items() if v == key), None)
                    if tag_id:
                        exif[tag_id] = value
                image_copy.exif = exif
            image_copy.save(save_path)    
        return True
    except Exception:
        return False

def transfer_metadata(
    output_fields: List[Any], 
    metadata: Dict[str, Any],
    propertysheet_map: Optional[Dict[int, Dict[str, Any]]] = None,
    gradio_component_map: Optional[Dict[int, str]] = None,
    remove_prefix_from_keys: bool = False
) -> List[Any]:
    """
    Maps a flat metadata dictionary to a list of Gradio UI components, with
    flexible and powerful matching logic for all component types.

    This function is UI-agnostic. For PropertySheets, it uses the `propertysheet_map`
    to reconstruct nested dataclass instances. It intelligently builds the expected
    metadata keys by interpreting the `prefixes` list: strings found as keys in the
    `metadata` are replaced by their values, while other strings are used literally.

    For standard Gradio components, it uses a three-tiered priority system:
    1.  **Explicit Mapping (Highest Priority):** If `gradio_component_map` is provided,
        it uses the specified metadata key for a given component ID.
    2.  **Base Label Matching:** If `remove_prefix_from_keys=True` and no explicit map
        is found, it matches the component's `.label` against "base" (prefix-stripped)
        metadata keys.
    3.  **Exact Label Matching (Default):** Otherwise, it attempts an exact match
        between the component's `.label` and a metadata key.

    Args:
        output_fields (List[Any]): The list of Gradio components to be updated.
        metadata (Dict[str, Any]): The flat dictionary of metadata from an image.
        propertysheet_map (Optional[Dict[int, Dict[str, Any]]]): 
            A map from a PropertySheet's `id()` to its configuration dict, which
            should contain its `type` and a list of `prefixes`.
        gradio_component_map (Optional[Dict[int, str]]):
            An optional map from a standard component's `id()` to the exact
            metadata key that should populate it.
        remove_prefix_from_keys (bool): If True, enables fallback matching
            by stripping prefixes from metadata keys for standard components.

    Returns:
        List[Any]: A list of `gr.update` or `gr.skip()` objects.
    """
    if propertysheet_map is None: propertysheet_map = {}
    if gradio_component_map is None: gradio_component_map = {}
        
    output_values = [None] * len(output_fields)
    component_to_index = {id(comp): i for i, comp in enumerate(output_fields)}

    # Pre-process metadata to create a map of base labels if needed.
    base_label_map = {}
    if remove_prefix_from_keys:
        base_label_map = {key.rsplit(' - ', 1)[-1]: value for key, value in metadata.items()}
    
    for component in output_fields:
        comp_id = id(component)
        output_index = component_to_index.get(comp_id)
        if output_index is None:
            continue
            
        # --- Logic for PropertySheets ---
        if comp_id in propertysheet_map:
            sheet_info = propertysheet_map[comp_id]
            dc_type = sheet_info.get("type")
            prefix_definitions = sheet_info.get("prefixes", [])
        
            # Build the list of actual prefix strings by interpreting the definitions.
            prefix_values = []
            for p_def in prefix_definitions:
                # If the prefix definition is a key in the metadata, use its value.
                if p_def in metadata:
                    prefix_values.append(str(metadata[p_def]))
                # Otherwise, treat it as a literal string.
                else:
                    prefix_values.append(p_def)
            
            prefix_values = [p for p in prefix_values if p]

            if not dc_type or not is_dataclass(dc_type):
                continue
            
            # Build the map from the dataclass structure to the expected full metadata keys.
            path_to_key_map = build_path_to_metadata_key_map(dc_type, prefix_values)
            
            # Get the base instance to start populating.
            instance_to_populate = getattr(component, '_dataclass_value', dc_type())
            if not is_dataclass(instance_to_populate):
                 instance_to_populate = dc_type()

            # Populate the instance by iterating through the path map.
            for path, metadata_key in path_to_key_map.items():
                if metadata_key in metadata:
                    value_from_meta = metadata[metadata_key]
                    
                    parts = path.split('.')
                    obj_to_set = instance_to_populate
                    try:
                        for part in parts[:-1]:
                            obj_to_set = getattr(obj_to_set, part)
                        
                        final_field_name = parts[-1]                        
                        converted_value = infer_type(value_from_meta)                           
                        setattr(obj_to_set, final_field_name, converted_value)
                    except (AttributeError, KeyError, ValueError, TypeError) as e:
                        print(f"Warning (transfer_metadata): Could not set value for path '{path}'. Error: {e}")
            
            output_values[output_index] = instance_to_populate
            
        # --- Unified Logic for Standard Gradio Components ---
        else:
            value_to_set = None
            
            # Priority 1: Check for an explicit mapping via gradio_component_map.
            if comp_id in gradio_component_map:
                metadata_key = gradio_component_map[comp_id]
                if metadata_key in metadata:
                    value_to_set = metadata[metadata_key]
            
            # If no explicit mapping was found, proceed to label-based matching.
            if value_to_set is None:
                label = getattr(component, 'label', None)
                if label:
                    # Priority 2: Check for a base label match if the flag is set.
                    if remove_prefix_from_keys and label in base_label_map:
                        value_to_set = base_label_map[label]
                    # Priority 3: Fallback to an exact label match.
                    elif label in metadata:
                        value_to_set = metadata[label]

            # If a value was found by any method, create the update object.
            if value_to_set is not None:
                output_values[output_index] = infer_type(value_to_set)
    
    return output_values