"""
File containing the boilerplate pyramid server
"""

import os
import json
import shutil
import traceback
import uuid

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.response import Response, FileResponse

from src.converter.main import parse_file


def get_main_page(request):
    """
    Get the root file main page
    :param request: The request
    :return: The response containing the WebInterface
    """
    print(request)
    here = os.path.dirname(os.path.abspath(__file__))
    response = FileResponse(
        os.path.join(here, 'files/WebInterface.html'),
        request = request,
        content_type = 'text/html'
    )
    return response


def get_file(request):
    """
    Function for the data sets that returns the data sets as files
    """
    print(request)
    here = os.path.dirname(os.path.abspath(__file__))
    response = FileResponse(
        os.path.join(here, f'files/{request.GET["name"]}'),
        request = request,
        content_type = 'application/json'
    )
    return response


def file_upload(request):
    """
    Function for the data sets that returns the data sets as files
    """

    filename = request.POST['file'].filename
    input_file = request.POST['file'].file
    uuid_ = uuid.uuid4()
    file_path = os.path.join('/tmp', '%s.csv' % uuid_)
    temp_file_path = file_path + '~'

    input_file.seek(0)
    with open(temp_file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)

    save_file = os.path.join('/tmp', '%s.ics' % uuid_)
    parse_file(temp_file_path, save_file = save_file)

    response = FileResponse(
        save_file,
        request = request,
        content_type = 'text/calendar'
    )
    response.content_disposition = 'attachment; filename=%s' % filename.replace('.csv', '.ics')
    return response


def get_parse_request(request: Request):
    """
    Handels the language parse request
    :param request: The request
    :return: The parse setnece or an exception
    """
    request = json.loads(request.body.decode("utf-8"))
    sentence = request['sentence']


def start_web_server():
    with Configurator() as config:
        config.add_route('main', '/')
        config.add_route('solve-request', '/solve-request')
        config.add_route('file-upload', '/file-upload')
        config.add_route('language-request', '/language-request')

        config.add_view(get_main_page, route_name = 'main')
        config.add_view(get_parse_request, route_name = 'solve-request')
        config.add_view(file_upload, route_name = 'file-upload', http_cache = 0)

        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6544, app)
    print("Go to: http://localhost:6544")
    server.serve_forever()
