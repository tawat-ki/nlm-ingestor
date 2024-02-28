import base64
from copy import deepcopy
from google.api_core.client_options import ClientOptions
# import PIL
import os
import json
import requests
from google.cloud import documentai
from google.cloud.documentai_toolbox import document


def get_bbox(points):
    y = []
    x = []
    for point in points:
        x.append(point.get('x', 0))
        y.append(point.get('y', 0))
    return [min(x), min(y), max(x), max(y)]


def segments_to_text(segments, text: str) -> str:
    """
    Document AI identifies text in different parts of the document by their
    offsets in the entirety of the document"s text. This function converts
    offsets to a string.
    """
    # If a text segment spans several lines, it will
    # be stored in different text segments.

    return "".join(
        text[int(segment.get('startIndex', '0')):
             int(segment.get('endIndex'))]
        for segment in segments
    )


def convert_document_to_hocr(documentai_document, document_title):
    wrapped_document = document.Document.from_documentai_document(
            documentai_document)

    # Converting wrapped_document to hOCR format
    hocr_string = wrapped_document.export_hocr_str(title=document_title)

    print("Document converted to hOCR!")
    return hocr_string


class GoogleOCR:

    def __init__(self, access_token=None, api_endpoint=None,
                 location=None, project_id=None, processor_id=None):
        self.access_token = access_token
        if api_endpoint is not None:
            self.api_endpoint = api_endpoint
        else:
            self.api_endpoint = (
                    f"https://{location}-documentai.googleapis.com/v1/"
                    f"projects/{project_id}/locations/{location}/processors"
                    f"/{processor_id}:process")
        temp_path = '/'.join(self.api_endpoint.split("/")[4:])
        self.api_endpoint_base = self.api_endpoint.split("/")[2]
        self.processor_path = temp_path.split(':')[0]

        self.field_mask = "text,pages.dimension,pages.tokens"

    def request_pylib(self,
                      filepath: str,
                      mime_type="application/pdf") -> list:
        # Instantiates a client
        docai_client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(
                api_endpoint=self.api_endpoint_base)
        )

        # Read the file into memory
        with open(filepath, "rb") as image:
            image_content = image.read()
        # Load Binary Data into Document AI RawDocument Object
        raw_document = documentai.RawDocument(content=image_content,
                                              mime_type=mime_type)

        # Configure the process request
        request = documentai.ProcessRequest(name=self.processor_path,
                                            raw_document=raw_document)

        # Use the Document AI client to process the sample form
        result = docai_client.process_document(request=request)


        return result.document

    def request_rest(self, filepath: str, mime_type="application/pdf") -> list:
        with open(filepath, "rb") as f:
            encoded_pdf = base64.b64encode(f.read()).decode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        request_data = {
                "skipHumanReview": True,
                "rawDocument": {
                    "mimeType": mime_type,
                    "content": encoded_pdf
                    },
                "fieldMask": self.field_mask
                }
        response = requests.post(self.api_endpoint,
                                 headers=headers,
                                 data=json.dumps(request_data))
        try:
            response.raise_for_status()
            result = response.json()
            return result['document']
        except requests.exceptions.HTTPError as err:
            print(f"Error: {err}")

    def request(self, fp: str, mime_type="application/pdf") -> list:
        if self.access_token is not None:
            return self.request_rest(filepath=fp, mime_type=mime_type)
        document_object = self.request_pylib(filepath=fp, mime_type=mime_type)
        document_json = json.loads(
                documentai.Document.to_json(document_object))
        return document_json

    # def __call__(self, img: PIL.Image.Image) -> list[dict]:
    #     return self.image_to_boxes(img)

    # def image_to_boxes(self, img: PIL.Image.Image) -> list[dict]:
    #     root_path = './temp'
    #     os.makedirs(root_path, exist_ok=True)
    #     temp_fp = os.path.join(root_path, './google_ocr_temp.jpg')
    #     img.save(temp_fp)

    #     document_object = self.request(temp_fp, "image/jpeg")
    #     text = document_object['text']
    #     tokens_list = []
    #     for page_num, page in enumerate(document_object['pages']):
    #         tokens = page['tokens']
    #         for token_num, token in enumerate(tokens):

    #             token_text = segments_to_text(
    #                     token['layout']['textAnchor']['textSegments'],
    #                     text)
    #             points = token['layout']['boundingPoly']['vertices']
    #             bbox = get_bbox(points)
    #             tokens_list.append({'bbox': bbox, 'text': token_text})
    #     return tokens_list
