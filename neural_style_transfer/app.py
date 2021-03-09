from IPython.display import display, clear_output
import ipywidgets as widgets
import requests
from .model import transform_images, run_transfer


def run_app():
    uploaded = False
    transferred = False
    urls = True

    url_btn = widgets.Button(description="Submit URLs", button_style="info")
    img_btn = widgets.Button(description="Submit Image Files", button_style="info")

    style_url, content_url = (
        widgets.Text(placeholder="Style Image URL"),
        widgets.Text(placeholder="Content Image URL"),
    )
    submit_btn = widgets.Button(
        description="Submit URLs", button_style="success", disabled=True
    )

    style_upload, content_upload = (
        widgets.FileUpload(multiple=False, description="Style Image"),
        widgets.FileUpload(multiple=False, description="Content Image"),
    )

    transfer_btn = widgets.Button(
        description="Run style transfer...", button_style="success"
    )
    finish_btn = widgets.Button(description="Reset", button_style="warning")
    new_crop_btn = widgets.Button(description="New Crop", button_style="danger")

    style_img, content_img = None, None
    style_img_raw, content_img_raw = None, None
    style_img_preview, content_img_preview = None, None

    def on_selection(b):
        nonlocal style_url, content_url, urls
        clear_output(wait=True)
        if b.description == "Submit URLs":
            style_url.observe(on_type_url, names="value")
            content_url.observe(on_type_url, names="value")
            display(widgets.VBox([style_url, content_url]))
            display(submit_btn)
        else:
            urls = False
            style_upload.observe(on_upload_change, names="_counter")
            content_upload.observe(on_upload_change, names="_counter")

            print("Upload your style image and content image:")
            display(widgets.HBox([style_upload, content_upload]))

    def on_type_url(change):
        nonlocal style_url, content_url, submit_btn
        if style_url.value and content_url.value:
            submit_btn.disabled = False
            submit_btn.on_click(on_submit_url)

    def on_submit_url(b):
        nonlocal style_url, content_url, submit_btn, style_img, content_img, style_img_preview, content_img_preview, style_img_raw, content_img_raw
        submit_btn.disabled = True
        try:
            style_img_raw = requests.get(style_url.value, stream=True).raw.read()
            content_img_raw = requests.get(content_url.value, stream=True).raw.read()
            style_img, content_img = transform_images(style_img_raw, content_img_raw)
            style_img_preview = widgets.Image(
                value=style_img, layout=widgets.Layout(width="512px")
            )
            content_img_preview = widgets.Image(
                value=content_img, layout=widgets.Layout(width="512px")
            )
            display(widgets.HBox([style_img_preview, content_img_preview]))
            new_crop_btn.on_click(on_new_crop)
            display(new_crop_btn)
            transfer_btn.on_click(on_transfer)
            display(transfer_btn)
        except Exception as e:
            print(e)
            style_url.value = ""
            content_url.value = ""

    def on_upload_change(change):
        nonlocal uploaded, style_upload, content_upload, style_img, content_img, style_img_preview, content_img_preview
        if style_upload.data and content_upload.data and not uploaded:
            uploaded = True
            style_upload.disabled = True
            content_upload.disabled = True
            style_img, content_img = transform_images(
                style_upload.data[0], content_upload.data[0]
            )
            style_img_preview = widgets.Image(
                value=style_img, layout=widgets.Layout(width="512px")
            )
            content_img_preview = widgets.Image(
                value=content_img, layout=widgets.Layout(width="512px")
            )
            display(widgets.HBox([style_img_preview, content_img_preview]))
            new_crop_btn.on_click(on_new_crop)
            display(new_crop_btn)
            transfer_btn.on_click(on_transfer)
            display(transfer_btn)

    def on_new_crop(b):
        nonlocal style_img, content_img, style_img_preview, content_img_preview, new_crop_btn, transfer_btn, style_img_raw, content_img_raw, urls
        style_img_preview.close()
        content_img_preview.close()
        new_crop_btn.close()
        transfer_btn.close()
        if urls:
            style_img, content_img = transform_images(style_img_raw, content_img_raw)
        else:
            style_img, content_img = transform_images(
                style_upload.data[0], content_upload.data[0]
            )
        style_img_preview = widgets.Image(
            value=style_img, layout=widgets.Layout(width="512px")
        )
        content_img_preview = widgets.Image(
            value=content_img, layout=widgets.Layout(width="512px")
        )
        new_crop_btn = widgets.Button(description="New Crop", button_style="danger")
        new_crop_btn.on_click(on_new_crop)
        transfer_btn = widgets.Button(
            description="Run style transfer...", button_style="success"
        )
        transfer_btn.on_click(on_transfer)
        display(widgets.HBox([style_img_preview, content_img_preview]))
        display(new_crop_btn)
        display(transfer_btn)

    def on_transfer(b):
        nonlocal transferred, transfer_btn, finish_btn, content_img, style_img, new_crop_btn
        if not transferred and (content_img and style_img):
            new_crop_btn.disabled = True
            transferred = True
            transfer_btn.disabled = True
            print("Running style transfer...")
            output = run_transfer(style_img, content_img)
            output_img = widgets.Image(
                value=output, layout=widgets.Layout(width="512px")
            )
            display(output_img)
            finish_btn.on_click(on_finish)
            display(finish_btn)

    def on_finish(b):
        nonlocal transferred, uploaded, transfer_btn
        transferred = False
        uploaded = False
        clear_output(wait=True)
        transfer_btn.disabled = False
        run_app()

    url_btn.on_click(on_selection)
    img_btn.on_click(on_selection)
    display(widgets.HBox([url_btn, img_btn]))