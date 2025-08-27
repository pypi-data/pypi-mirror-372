from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Callable
import base64
from io import BytesIO
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import json
import uuid

# Tell streamlit that there is a component called streamlit_canvas_editor,
# and that the code to display that component is in the "frontend" folder
frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component(
    "streamlit_canvas_editor", path=str(frontend_dir)
)

def image_to_base64(image: Union[Image.Image, str, bytes]) -> str:
    """Convert an image to base64 string for the canvas component."""
    if isinstance(image, str):
        image = Image.open(image)
    elif isinstance(image, bytes):
        image = Image.open(BytesIO(image))

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def normalize_rectangles_to_component(rectangles: List[Dict[str, Any]], page_number: int = 1) -> List[Dict[str, Any]]:
    """Normalize rectangle dictionaries to the format expected by the component."""
    normalized: List[Dict[str, Any]] = []

    for i, rect in enumerate(rectangles):
        norm_rect: Dict[str, Any] = {}

        # Block_ID
        norm_rect["Block_ID"] = rect.get("Block_ID") or f"page_{page_number}_block_{i+1}"

        # Block_Type / content / id
        norm_rect["Block_Type"] = rect.get("Block_Type", "Text")
        norm_rect["Text_Content"] = rect.get("Text_Content", "")
        norm_rect["Text_ID"] = rect.get("Text_ID", "")

        # Coordinates
        bbox = rect.get("Boundary_Boxes")
        if isinstance(bbox, list) and len(bbox) == 4:
            x0, y0, x1, y1 = map(int, bbox)
            norm_rect["x"] = x0
            norm_rect["y"] = y0
            norm_rect["width"] = max(1, x1 - x0)
            norm_rect["height"] = max(1, y1 - y0)
            norm_rect["Boundary_Boxes"] = [x0, y0, x1, y1]
        else:
            # Fallback default position
            x, y, w, h = 10 + i * 20, 10 + i * 20, 100, 50
            norm_rect.update({"x": x, "y": y, "width": w, "height": h})
            norm_rect["Boundary_Boxes"] = [x, y, x + w, y + h]

        normalized.append(norm_rect)

    return normalized

def convert_component_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert component output to match your JSON format."""
    if not result:
        return result

    rects = result.get("rectangles")
    if rects is not None:
        formatted: List[Dict[str, Any]] = []
        for rect in rects:
            formatted.append({
                "Block_ID": rect.get("Block_ID", ""),
                "Block_Type": rect.get("Block_Type", "Text"),
                "Text_Content": rect.get("Text_Content", ""),
                "Text_ID": rect.get("Text_ID", ""),
                "Boundary_Boxes": rect.get("Boundary_Boxes", [0, 0, 0, 0]),
                "Image": None,
            })
        result["rectangles"] = formatted

    return result

def streamlit_canvas_editor(
    image: Optional[Union[Image.Image, str, bytes]] = None,
    rectangles: Optional[List[Dict[str, Any]]] = None,
    page_number: int = 1,
    height: int = 700,
    ocr_function: Optional[Callable[[Image.Image, List[int]], str]] = None,
    key: Optional[str] = None,
    _instance_id: Optional[str] = None,
    ocr_timeout_ms: int = 90000,  # configurable OCR timeout for JS
) -> Dict[str, Any]:
    """
    Streamlit Canvas Editor Component for drawing and editing rectangles on images.

    - `key` MUST be unique per instance in a Streamlit page.
    - `_instance_id` routes OCR requests/responses and namespaces session state.
    """
    # -------- instance id ----------
    if _instance_id is None:
        _instance_id = f"inst_{uuid.uuid4()}"

    # Namespaced session_state keys
    ocr_requests_key = f'ocr_requests:{_instance_id}'
    pending_resp_key = f'pending_ocr_response:{_instance_id}'

    if ocr_requests_key not in st.session_state:
        st.session_state[ocr_requests_key] = {}

    # Prepare image data if provided
    image_data = None
    image_for_ocr: Optional[Image.Image] = None
    if image is not None:
        if isinstance(image, str):
            image_for_ocr = Image.open(image)
        elif isinstance(image, bytes):
            image_for_ocr = Image.open(BytesIO(image))
        else:
            image_for_ocr = image
        image_data = image_to_base64(image_for_ocr)

    # Normalize rectangles to component format
    normalized_rectangles = normalize_rectangles_to_component(rectangles or [], page_number) if rectangles else None

    # OCR available only if both function and image exist
    ocr_available = (ocr_function is not None and image_for_ocr is not None)

    # Pull pending OCR response (if any) for this instance
    ocr_response_to_send = st.session_state.pop(pending_resp_key, None)

    # Call the frontend component
    component_value = _component_func(
        image_data=image_data,
        rectangles=normalized_rectangles,
        page_number=page_number,
        height=height,
        ocr_enabled=ocr_available,                # only true when we can actually run OCR
        ocr_response=ocr_response_to_send,        # instance-scoped response
        _instance_id=_instance_id,                # pass to JS
        ocr_timeout_ms=ocr_timeout_ms,            # pass timeout to JS
        key=key,
        default={
            "rectangles": [],
            "selected_index": -1,
            "canvas_width": 800,
            "canvas_height": 600,
            "ocr_request": None,
            "_instance_id": _instance_id,
        },
    )

    # If frontend asks OCR but OCR is unavailable, immediately respond with an error to avoid timeout
    if component_value and component_value.get('ocr_request'):
        ocr_req = component_value['ocr_request']
        inst_id_from_req = ocr_req.get('_instance_id') or component_value.get('_instance_id') or _instance_id

        if not ocr_available:
            st.session_state[f'pending_ocr_response:{inst_id_from_req}'] = {
                "text": "[OCR unavailable: no image or OCR function disabled]",
                "rect_index": int(ocr_req.get('rect_index', -1)),
                "request_id": ocr_req.get('request_id'),
                "success": False,
                "_instance_id": inst_id_from_req,
            }
            st.rerun()

    # Handle OCR request from frontend (for THIS instance only, when available)
    if component_value and component_value.get('ocr_request') and ocr_available:
        ocr_req = component_value['ocr_request']
        if ocr_req.get('_instance_id') == _instance_id:
            rect_index = int(ocr_req.get('rect_index', -1))
            bbox = ocr_req.get('bbox') or ocr_req.get('Boundary_Boxes')
            request_id = ocr_req.get('request_id')

            if bbox and request_id and image_for_ocr:
                if request_id not in st.session_state[ocr_requests_key]:
                    st.session_state[ocr_requests_key][request_id] = 'processing'

                    with st.spinner(f'🔍 Running OCR on block {rect_index + 1}...'):
                        progress_placeholder = st.empty()
                        try:
                            x0, y0, x1, y1 = map(int, bbox)
                            cropped_image = image_for_ocr.crop((max(0, x0), max(0, y0), x1, y1))

                            p = progress_placeholder.progress(25, text="Preprocessing image...")
                            extracted_text = ocr_function(cropped_image, [x0, y0, x1, y1])
                            p.progress(90, text="Finalizing...")

                            st.session_state[ocr_requests_key][request_id] = 'completed'
                            st.session_state[pending_resp_key] = {
                                "text": extracted_text,
                                "rect_index": rect_index,
                                "request_id": request_id,
                                "success": True,
                                "_instance_id": _instance_id,  # route back to correct JS instance
                            }

                            # Best-effort live update of component_value rectangles (optional)
                            if component_value and 'rectangles' in component_value:
                                if 0 <= rect_index < len(component_value['rectangles']):
                                    component_value['rectangles'][rect_index]['Text_Content'] = extracted_text

                            p.progress(100, text="OCR Complete!")
                            progress_placeholder.empty()

                            # Keep last 10 request statuses
                            if len(st.session_state[ocr_requests_key]) > 10:
                                for k in list(st.session_state[ocr_requests_key].keys())[:-10]:
                                    del st.session_state[ocr_requests_key][k]

                            st.success(f"✅ OCR completed for block {rect_index + 1}")
                            st.rerun()

                        except Exception as e:
                            st.session_state[ocr_requests_key][request_id] = 'error'
                            st.session_state[pending_resp_key] = {
                                "text": f"[OCR Error: {str(e)}]",
                                "rect_index": rect_index,
                                "request_id": request_id,
                                "success": False,
                                "_instance_id": _instance_id,
                            }
                            progress_placeholder.empty()
                            st.error(f"❌ OCR failed: {str(e)}")
                            st.rerun()

    return convert_component_output(component_value)

# ---------------- Demo app with TWO instances ----------------

def main():
    """Demo application showing two independent canvas editors with optional OCR."""
    st.set_page_config(page_title="Canvas Editor Demo (Two Instances)", layout="wide")
    st.title("📝 Document Block Extraction Editor — Two Independent Instances")

    # Dummy OCR (replace with real OCR)
    def demo_ocr_function(image: Image.Image, bbox: List[int]) -> str:
        import time, random
        time.sleep(0.4)
        w, h = image.width, image.height
        samples = [
            f"Extracted text from region ({w}x{h})",
            "Lorem ipsum dolor sit amet.",
            f"OCR block at ({bbox[0]}, {bbox[1]})",
            "Sample OCR output.",
        ]
        return random.choice(samples)

    st.session_state.setdefault('rects_A', [
        {"Block_ID": "block_1", "Block_Type": "PageHeader", "Text_Content": "Doc A Title", "Text_ID": "title_a", "Boundary_Boxes": [50, 50, 400, 100], "Image": None},
        {"Block_ID": "block_2", "Block_Type": "Text",       "Text_Content": "",            "Text_ID": "",        "Boundary_Boxes": [50, 120, 400, 180], "Image": None},
    ])
    st.session_state.setdefault('rects_B', [
        {"Block_ID": "block_1", "Block_Type": "PageHeader", "Text_Content": "Doc B Title", "Text_ID": "title_b", "Boundary_Boxes": [60, 60, 420, 110], "Image": None},
        {"Block_ID": "block_2", "Block_Type": "SectionHeader", "Text_Content": "",         "Text_ID": "hdr_b",   "Boundary_Boxes": [60, 130, 420, 170], "Image": None},
    ])

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Editor A")
        img_a = st.file_uploader("Upload image for Editor A", type=["png","jpg","jpeg"], key="uploader_A")
        pil_a = Image.open(img_a) if img_a else None

        res_a = streamlit_canvas_editor(
            image=pil_a,
            rectangles=st.session_state['rects_A'],
            page_number=1,
            height=700,
            ocr_function=demo_ocr_function,     # set None to disable OCR on A
            key="canvas_A",                      # unique Streamlit key
            _instance_id="editor_A",             # unique route id
            ocr_timeout_ms=90000,
        )
        if res_a and res_a.get('rectangles') is not None:
            old = json.dumps(st.session_state['rects_A'], sort_keys=True)
            new = json.dumps(res_a['rectangles'], sort_keys=True)
            if old != new:
                st.session_state['rects_A'] = res_a['rectangles']
        st.caption(f"Blocks A: {len(st.session_state['rects_A'])}")

    with colB:
        st.subheader("Editor B")
        img_b = st.file_uploader("Upload image for Editor B", type=["png","jpg","jpeg"], key="uploader_B")
        pil_b = Image.open(img_b) if img_b else None

        res_b = streamlit_canvas_editor(
            image=pil_b,
            rectangles=st.session_state['rects_B'],
            page_number=1,
            height=700,
            ocr_function=demo_ocr_function,     # set None to disable OCR on B
            key="canvas_B",                      # unique Streamlit key
            _instance_id="editor_B",             # unique route id
            ocr_timeout_ms=90000,
        )
        if res_b and res_b.get('rectangles') is not None:
            old = json.dumps(st.session_state['rects_B'], sort_keys=True)
            new = json.dumps(res_b['rectangles'], sort_keys=True)
            if old != new:
                st.session_state['rects_B'] = res_b['rectangles']
        st.caption(f"Blocks B: {len(st.session_state['rects_B'])}")

    with st.expander("📥 Export JSON (Editor A)", expanded=False):
        st.download_button(
            "Download A JSON",
            data=json.dumps(st.session_state['rects_A'], indent=2),
            file_name="editor_A_blocks.json",
            mime="application/json",
        )

    with st.expander("📥 Export JSON (Editor B)", expanded=False):
        st.download_button(
            "Download B JSON",
            data=json.dumps(st.session_state['rects_B'], indent=2),
            file_name="editor_B_blocks.json",
            mime="application/json",
        )

if __name__ == "__main__":
    main()
