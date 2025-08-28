# Copyright (c) 2025. Verimatrix. All Rights Reserved.
# All information in this file is Verimatrix Confidential and Proprietary.
'''Sending commands to APS API'''
import json
import logging
import os
import shutil
import time
import mimetypes
from datetime import datetime
import dateutil.parser

from .aps_utils import ApsUtils
from .aps_requests import ApsRequest

LOGGER = logging.getLogger(__name__)

OPENAPI_VERSION = '2.6.0'

PROTECT_STATES = ['protect_queue', 'protect_in_progress']

DEFAULT_SUBSCRIPTION_TYPE_XTD = "XTD_PLATFORM"

# S3 multipart upload has a minimum part size of 5Mb
PART_SIZE=5242880

def upload_data(url, data):
    '''Upload data to S3'''
    return ApsRequest.put(url, data=data)

def construct_headers(token):
    '''Construct HTTP headers to be sent in all requests to APS API endpoint'''
    version = OPENAPI_VERSION
    headers = {}
    headers['Authorization'] = token
    headers['Accept'] = f'application/vnd.aps.appshield.verimatrixcloud.net;version={version}'
    return headers


class ApsApi():
    '''Class for sending commands to APS REST API'''

    utils = ApsUtils()

    def __init__(self, **kwargs):

        self.api_key = kwargs.pop('api_key', None)
        self.api_gateway_url = kwargs.pop('api_gateway_url', None) or 'https://aps-api.appshield.verimatrixcloud.net'
        self.access_token_url = kwargs.pop('access_token_url', None) or 'https://ssoapi-ng.platform.verimatrixcloud.net/v1/token'
        self.wait_seconds = kwargs.pop('wait_seconds', 0)

        self.authenticated = False
        self.tokenExpiration = 0
        self.headers = None

    def is_authenticated(self):
        '''Have we authenticated'''
        return self.authenticated

    def ensure_authenticated(self):
        if not self.authenticated:
            '''Not authenticated'''
            LOGGER.debug(f'Not authenticated yet, will proceed to get token')
            self.provide_token()

        current_time = time.time()
        LOGGER.debug(f'Evaluating needs to re-authenticate {self.tokenExpiration} vs {current_time}')

        if self.authenticated and (current_time + 45 > self.tokenExpiration):
            '''Token about to expire, will authenticate'''
            LOGGER.debug(f'Authenticated but token will expire shortly, will proceed to get token')
            self.provide_token()


    def provide_token(self):
        '''Authenticate using API Key'''
        token, tokenExpiration = self.utils.authenticate_api_key(self.access_token_url, self.api_key)

        if tokenExpiration != None:
            self.tokenExpiration = time.time() + tokenExpiration
            LOGGER.info(f'New token expires in {tokenExpiration} seconds')

        self.headers = construct_headers(token)
        self.authenticated = True

    def get_account_info(self):
        '''Return account info'''
        url = f'{self.api_gateway_url}/report/account'
        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers)
        LOGGER.debug(f'Response headers: {response.headers}')
        LOGGER.debug(f'Get account info response: {response.json()}')
        return response.json()

    def add_application(self, name, package_id, os_name, permissions, group=None, subscription_type=None):
        '''Add an application'''
        url = f'{self.api_gateway_url}/applications'

        body = {}
        body['applicationName'] = name
        body['applicationPackageId'] = package_id
        body['permissionPrivate'] = permissions['private']
        body['permissionUpload'] = False if permissions['private'] else not permissions['no_upload']
        body['permissionDelete'] = False if permissions['private'] else not permissions['no_delete']
        body['os'] = os_name
        if group:
            body['group'] = group
        body['subscriptionType'] = subscription_type if subscription_type else DEFAULT_SUBSCRIPTION_TYPE_XTD        
        self.ensure_authenticated()
        response = ApsRequest.post(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Post application response: {response.json()}')
        return response.json()

    def update_application(self, application_id, name, permissions):
        '''Update an application'''
        url = f'{self.api_gateway_url}/applications/{application_id}'

        body = {}
        body['applicationName'] = name
        body['permissionPrivate'] = permissions['private']
        body['permissionUpload'] = False if permissions['private'] else not permissions['no_upload']
        body['permissionDelete'] = False if permissions['private'] else not permissions['no_delete']
        self.ensure_authenticated()
        response = ApsRequest.patch(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Update application response: {response.json()}')
        return response.json()

    def list_applications(self, application_id, group=None, subscription_type=None):
        '''List applications'''
        params = {}
        
        params['subscriptionType'] = subscription_type if subscription_type else DEFAULT_SUBSCRIPTION_TYPE_XTD

        if application_id:
            url = f'{self.api_gateway_url}/applications/{application_id}'
        else:
            url = f'{self.api_gateway_url}/applications'
            if group:
                params['group'] = group

        # If not searching by application_id this operation on DynamoDB is Eventually Consistent
        # so wait some time before starting (to ensure system tests using this module behave
        # reliably).
        if not application_id and self.wait_seconds:
            time.sleep(self.wait_seconds)

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers, params=params)
        LOGGER.debug(f'Response headers: {response.headers}')
        LOGGER.debug(f'Get applications response: {response.json()}')
        return response.json()

    def delete_application(self, application_id):
        '''Delete an aplication'''
        params = {}
        params['id'] = application_id

        url = f'{self.api_gateway_url}/applications/{application_id}'

        self.ensure_authenticated()
        response = ApsRequest.delete(url, headers=self.headers)
        LOGGER.debug(f'Delete application response: {response.json()}')
        return response.json()

    def list_builds(self, application_id, build_id, subscription_type=None):
        '''List builds'''
        params = {}
        if build_id:
            url = f'{self.api_gateway_url}/builds/{build_id}'
        else:
            url = f'{self.api_gateway_url}/builds'
            if application_id:
                params['app'] = application_id

        params['subscriptionType'] = subscription_type if subscription_type else DEFAULT_SUBSCRIPTION_TYPE_XTD

        # If not searching by build_id this operation on DynamoDB is Eventually Consistent
        # so wait some time before starting (to ensure system tests using this module behave
        # reliably).
        if not build_id and self.wait_seconds:
            time.sleep(self.wait_seconds)

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers, params=params)
        builds = response.json()
        LOGGER.debug(f'Listing builds for app_id:{application_id} build_id:{build_id} - {builds}')
        return builds

    def create_build(self, application_id=None, subscription_type=None):
        '''Create a new build'''
        url = f'{self.api_gateway_url}/builds'

        # Create a new build
        body = {}
        if application_id:
            body['applicationId'] = application_id

        body['subscriptionType'] = subscription_type if subscription_type else DEFAULT_SUBSCRIPTION_TYPE_XTD
        
        self.ensure_authenticated()
        response = ApsRequest.post(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Post build response: {response.json()}')
        return response.json()

    def set_build_metadata(self, build_id, file):
        '''Set build metadata'''
        version_info = self.utils.extract_version_info(file)

        # Inform the backend the file is going to be uploaded
        url = f'{self.api_gateway_url}/builds/{build_id}/metadata'

        body = {}
        body['os'] = 'ios' if file.endswith('.xcarchive.zip') else 'android'
        body['osData'] = version_info
        self.ensure_authenticated()
        response = ApsRequest.put(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Set build metadata response: {response.json()}')
        return response.json()

    def update_build_metadata(self, build_id, sign_final_binary=False):
        '''Update build metadata'''

        url = f'{self.api_gateway_url}/builds/{build_id}/metadata'

        body = {}
        body['signFinalBinary'] = sign_final_binary

        self.ensure_authenticated()
        response = ApsRequest.post(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Update build metadata response: {response.json()}')
        return response.json()

    def upload_start(self, build_id, file, artifact_type=None):
        '''Start a multipart upload. Returns the upload_id and upload_name'''
        data, upload_name = self.upload_start_full(build_id, file, artifact_type)
        upload_id = data['UploadId']

        return (upload_id, upload_name)

    def upload_start_full(self, build_id, file, artifact_type=None):
        '''Start a multipart upload. Returns full response'''
        url =  f'{self.api_gateway_url}/uploads/{build_id}/start-upload'

        upload_name = os.path.basename(file)

        # mime type
        upload_type = mimetypes.guess_type(file)[0]
        if not upload_type:
            upload_type = 'application/zip'

        params = {
            'uploadName': upload_name,
            'uploadType': upload_type,
        }
        if artifact_type:
            params['artifactType'] = artifact_type

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers, params=params)
        data = response.json()

        return data, upload_name

    def upload_complete(self, build_id, upload_id, upload_name, upload_parts, artifact_type=None):
        '''Complete a multipart upload'''
        url =  f'{self.api_gateway_url}/uploads/{build_id}/complete-upload'
        body =  {
            'parts': upload_parts,
            'uploadId': upload_id,
            'uploadName': upload_name,
        }
        if artifact_type:
            body['artifactType'] = artifact_type

        self.ensure_authenticated()
        response = ApsRequest.post(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Complete upload response: {response.json()}')

    def upload_abort(self, build_id, upload_id, upload_name, message=None, artifact_type=None):
        '''Abort a multipart upload'''
        url =  f'{self.api_gateway_url}/uploads/{build_id}/abort-upload'
        body =  {
            'uploadId': upload_id,
            'uploadName': upload_name,
        }
        if message:
            body['message'] = message
        if artifact_type:
            body['artifactType'] = artifact_type

        self.ensure_authenticated()
        response = ApsRequest.post(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Abort upload response: {response.json()}')

    def upload_part(self, build_id, upload_id, upload_name, part_number, data):
        '''Upload a single part of the multipart upload. Returns etag information needed
        for the upload complete operation'''
        url =  f'{self.api_gateway_url}/uploads/{build_id}/get-upload-url'
        params = {
            'uploadName': upload_name,
            'partNumber': part_number,
            'uploadId': upload_id
        }

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers, params=params)
        LOGGER.debug(f'Get upload url response: {response.text}')

        # Upload the data
        response = upload_data(response.text, data)

        # Return the Etag and PartNumber
        return {
            'ETag': response.headers['ETag'],
            'PartNumber': part_number
        }

    def multipart_upload(self, build_id, file, artifact_type=None):
        '''Multipart upload method'''

        LOGGER.info(f'Uploading application {file}')

        upload_id = upload_name = None
        try:
            upload_id, upload_name = self.upload_start(build_id, file, artifact_type)

            # Split file into parts. For each part, get an upload url and upload
            # the part. Part numbers start at 1. After uploading each part, save
            # the returned ETag header. We need that when completing the upload.
            parts = []
            part_number = 1
            with open(file, 'rb') as fp:
                while True:
                    data = fp.read(PART_SIZE)
                    if not data:
                        break
                    part = self.upload_part(build_id, upload_id, upload_name, part_number, data)

                    parts.append(part)
                    # Increment the part number and repeat until the file is read.
                    part_number += 1


            # Complete the upload
            self.upload_complete(build_id, upload_id, upload_name, parts, artifact_type)
            return True
        except Exception as e:
            LOGGER.warning(f'Upload method failed: {e}')
            if upload_id and upload_name:
                self.upload_abort(build_id, upload_id, upload_name, artifact_type)
            return False

    def add_build(self, file, application_id=None, set_metadata=True, upload=True, subscription_type=None):
        '''Add a new build'''
        response = self.create_build(application_id, subscription_type)
        if 'errorMessage' in response:
            return response

        build_id = response['id']

        if set_metadata:
            response = self.set_build_metadata(build_id, file)
            if 'errorMessage' in response:
                LOGGER.debug('set build metadata failed, delete build')
                self.delete_build(build_id)
                return response

        # If the application_id is not set, then we do not upload the binary
        # (upload of the binary requires that the build is associated to an app).
        if not application_id or not upload:
            return response

        if not self.multipart_upload(build_id, file):
            LOGGER.debug('upload failed, delete build')
            self.delete_build(build_id)
        return response

    def add_build_without_app(self, file, set_metadata=True, subscription_type=None):
        '''Add a new build that is not yet associated to an application'''

        return self.add_build(file,
                              application_id=None,
                              set_metadata=set_metadata,
                              upload=False,
                              subscription_type=subscription_type)

    def delete_build(self, build_id):
        '''Delete a build'''
        url = f'{self.api_gateway_url}/builds/{build_id}'

        self.ensure_authenticated()
        response = ApsRequest.delete(url, headers=self.headers)
        LOGGER.debug(f'Delete build response: {response.json()}')
        return response.json()

    def delete_build_ticket(self, build_id, ticket_id):
        '''Delete a Zendesk ticket associated to a build'''
        url = f'{self.api_gateway_url}/builds/{build_id}'

        params = {}
        params['cmd'] = 'delete-ticket'
        params['ticket'] = ticket_id
        self.ensure_authenticated()
        response = ApsRequest.patch(url, headers=self.headers, params=params)
        LOGGER.debug(f'Delete build ticket response: {response.json()}')
        return response.json()

    def get_build_ticket(self, build_id, ticket_id):
        '''Get the Zendesk ticket details'''
        url = f'{self.api_gateway_url}/builds/{build_id}'

        params = {}
        params['ticket'] = ticket_id

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers, params=params)
        LOGGER.debug(f'Get build ticket response: {response.json()}')
        return response.json()

    def protect_start(self, build_id):
        '''Initiate build protection'''
        url = f'{self.api_gateway_url}/builds/{build_id}'

        params = {}
        params['cmd'] = 'protect'

        self.ensure_authenticated()
        response = ApsRequest.patch(url, headers=self.headers, params=params)
        LOGGER.debug(f'Protect start response: {response.json()}')
        return response.json()

    def protect_get_status(self, build_id):
        '''Get the protection status of a build'''
        return self.list_builds(None, build_id, None)

    def protect_cancel(self, build_id):
        '''Cancel a protection job'''
        url = f'{self.api_gateway_url}/builds/{build_id}'

        params = {}
        params['cmd'] = 'cancel'

        self.ensure_authenticated()
        response = ApsRequest.patch(url, headers=self.headers, params=params)
        LOGGER.debug(f'Protect cancel response: {response.json()}')
        return response.json()

    def protect_download(self, build_id):
        '''Download a protected build file'''
        # Request a S3 presigned URL for the download
        url = f'{self.api_gateway_url}/builds/{build_id}'

        params = {}
        params['url'] = 'protected'

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers, params=params)
        LOGGER.debug(f'Protect get download URL, response: {response.text}')

        # Now download the protected binary.
        url = response.text
        local_filename = url.split('/')[-1]
        local_filename = local_filename.split('?')[0]
        LOGGER.info('Starting download of protected file')

        self.ensure_authenticated()
        response = ApsRequest.get(url, stream=True)
        LOGGER.debug(f'Download protection file response: {response}')
        with open(local_filename, 'wb') as file_handle:
            shutil.copyfileobj(response.raw, file_handle)
        LOGGER.info(f'Protected file downloaded to {local_filename}')

        result_file = open('protect_result.txt', 'w')
        result_file.write(local_filename)
        result_file.close()

    def add_build_to_application(self, build_id, application_id):
        '''Associate a build to an application'''
        url = f'{self.api_gateway_url}/builds/{build_id}/app'

        body = {}
        body['applicationId'] = application_id

        self.ensure_authenticated()
        response = ApsRequest.put(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Add build to application response: {response.json()}')
        return response.json()

    def protect_build(self, build_id):
        '''High level protect build command.
        This operation does the following
        - protect_start
        - poll protection state (protect_get_status) until protection is completed'''

        LOGGER.info(f'Starting protection for build {build_id}')

        # Start protection
        response = self.protect_start(build_id)
        if 'errorMessage' in response:
            LOGGER.debug('protection start call failed, delete build')
            self.delete_build(build_id)
            return False

        LOGGER.info(f'Protection stated, will wait for completion of build {build_id}')

        while True:
            build = self.protect_get_status(build_id)

            if not 'state' in build.keys():
                LOGGER.info(f'Failed to get protect status for build {build_id}')
                LOGGER.info(build)
                return False

            if build['state'] not in PROTECT_STATES:
                LOGGER.info('Protection complete')
                break
            if build['state'] == 'protect_queue':
                LOGGER.info('In protect queue..')
            else:
                if 'progressData' in build:
                    LOGGER.info(f'Protecting {build["progressData"]["progress"]} complete')
            time.sleep(10)

        return (build['state'] == 'protect_done')


    def protect(self, file, subscription_type=None, signing_certificate=None, secondary_signing_certificate=None, mapping_file=None, build_protection_configuration=None, build_certificate_pinning_configuration=None):
        '''High level protect command.
        This operation does the following
        - add_build
        - protect_start
        - poll protection state (protect_get_status) until protection is completed
        - protect_download'''

        # First add the build
        build = self.add_build_without_app(file, subscription_type=subscription_type)
        if 'errorMessage' in build:
            LOGGER.error(f'Failed to add new build {build["errorMessage"]}')
            return False

        application_package_id = build['applicationPackageId']
        os_type = self.utils.get_os(file)

        applications = self.list_applications(application_id=None,
                                              group=None,
                                              subscription_type=subscription_type)
        application = None

        # Check if we have an app for this build (by searching for a matching
        # applicationPackageId)
        for app in applications:
            if app['applicationPackageId'] == application_package_id \
               and app['os'] == os_type:
                application = app
                break

        # If no application for the build exists then create a new app.
        # Take the applicationName from the package id and use default permissive permissions
        if not application:
            permissions = {}
            permissions['private'] = False
            permissions['no_upload'] = False
            permissions['no_delete'] = False

            application = self.add_application(application_package_id,
                                               application_package_id,
                                               os_type,
                                               permissions,
                                               subscription_type=subscription_type)
            if 'errorMessage' in application:
                LOGGER.error(f'Failed to add new application {application["errorMessage"]}')
                return False

        self.add_build_to_application(build['id'], application['id'])

        if signing_certificate:
            self.set_signing_certificate(application['id'], signing_certificate)
        if secondary_signing_certificate:
            self.set_secondary_signing_certificate(application['id'], secondary_signing_certificate)
        if mapping_file:
            self.set_mapping_file(build['id'], mapping_file)
        if build_protection_configuration:
            self.set_build_protection_configuration(build['id'], build_protection_configuration)
        if build_certificate_pinning_configuration:
            self.set_build_certificate_pinning_configuration(build['id'], build_certificate_pinning_configuration)

        # Upload the binary
        if not self.multipart_upload(build['id'], file):
            LOGGER.debug('upload failed, delete build')
            self.delete_build(build['id'])
            return False

        # Start protection

        if not self.protect_build(build['id']):
            LOGGER.info(f'Protection failed with build id:{build["id"]}')
            return False

        # Download the protected app on success.
        self.protect_download(build['id'])
        # This line is parsed by test-events-android to extract the build id. Do not change
        LOGGER.info(f'Protection succeeded with build id:{build["id"]}')

        return True

    def get_build_artifacts(self, build_id):
        '''Get build artifacts'''

        url = f'{self.api_gateway_url}/report/artifacts?buildId={build_id}'

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers)

        outdir = os.getcwd() + os.sep + build_id
        shutil.rmtree(outdir, ignore_errors=True)
        os.mkdir(outdir)

        artifact_urls = response.json()
        for url in artifact_urls:
            local_filename = url.split('/')[-1]
            local_filename = local_filename.split('?')[0]
            LOGGER.info(f'Downloading artifact {local_filename}')
            local_filename = outdir + os.sep + local_filename
            self.ensure_authenticated()
            response = ApsRequest.get(url, stream=True)
            with open(local_filename, 'wb') as file_handle:
                shutil.copyfileobj(response.raw, file_handle)
        LOGGER.info(f'Build artifacts downloaded to {outdir}')


    def get_statistics(self, start, end):
        '''Get APS statistics'''
        start_time = dateutil.parser.parse(start)
        if end:
            end_time = dateutil.parser.parse(end)
        else:
            end_time = datetime.now()

        params = {}

        url = f'{self.api_gateway_url}/report/statistics?start={start_time}&end={end_time}'
        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers, params=params)
        return response.json()

    def display_application_package_id(self, file):
        '''Extract the package id from the input file'''
        return self.utils.extract_package_id(file)

    def set_protection_configuration(self, application_id, file):
        '''Set protection configuration for an application'''
        url = f'{self.api_gateway_url}/applications/{application_id}/protection-configuration'

        body = {}
        if file:
            with open(file, 'rb') as file_handle:
                body['configuration'] = json.load(file_handle)
        self.ensure_authenticated()
        response = ApsRequest.put(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Set protection configuration response: {response.json()}')
        return response.json()

    def delete_protection_configuration(self, application_id):
        '''Delete protection configuration for an application'''

        url = f'{self.api_gateway_url}/applications/{application_id}/protection-configuration'

        self.ensure_authenticated()
        response = ApsRequest.delete(url, headers=self.headers)
        LOGGER.debug(f'Delete protection configuration response: {response.json()}')
        return response.json()

    def set_build_protection_configuration(self, build_id, file):
        '''Set protection configuration for a build'''
        url = f'{self.api_gateway_url}/builds/{build_id}/protection-configuration'

        body = {}
        if file:
            with open(file, 'rb') as file_handle:
                body['configuration'] = json.load(file_handle)

        self.ensure_authenticated()
        response = ApsRequest.put(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Set build protection configuration response: {response.json()}')
        return response.json()

    def delete_build_protection_configuration(self, build_id):
        '''Delete protection configuration for a build'''
        url = f'{self.api_gateway_url}/builds/{build_id}/protection-configuration'

        self.ensure_authenticated()
        response = ApsRequest.delete(url, headers=self.headers)
        LOGGER.debug(f'Delete build protection configuration response: {response.json()}')
        return response.json()

    def set_report_and_exit_flag(self, application_id, flagValue):
        '''Set report and exit flag for an application'''
        url = f'{self.api_gateway_url}/applications/{application_id}/report-and-exit?enabled={flagValue}'

        self.ensure_authenticated()
        response = ApsRequest.put(url, headers=self.headers)
        LOGGER.debug(f'Set report and exit flag for an application response: {response.json()}')
        return response.json()

    def set_signing_certificate(self, application_id, file):
        '''Set signing certificate for an application'''

        url = f'{self.api_gateway_url}/applications/{application_id}/signing-certificate'

        body = {}
        with open(file, 'r') as file_handle:
            body['certificate'] = file_handle.read()
            body['certificateFileName'] = os.path.basename(file)
        LOGGER.info(body)
        self.ensure_authenticated()
        response = ApsRequest.put(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Set signing certificate response: {response.json()}')
        return response.json()
    
    def delete_signing_certificate(self, application_id):
        '''Delete signing certificate for an application'''

        url = f'{self.api_gateway_url}/applications/{application_id}/signing-certificate'

        self.ensure_authenticated()
        response = ApsRequest.delete(url, headers=self.headers)
        LOGGER.debug(f'Delete signing certificate response: {response.json()}')
        return response.json()    

    def set_secondary_signing_certificate(self, application_id, file):
        '''Set secondary signing certificate for an application'''

        url = f'{self.api_gateway_url}/applications/{application_id}/secondary-signing-certificate'

        body = {}
        with open(file, 'r') as file_handle:
            body['certificate'] = file_handle.read()
            body['certificateFileName'] = os.path.basename(file)
        LOGGER.info(body)
        self.ensure_authenticated()
        response = ApsRequest.put(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Set secondary signing certificate response: {response.json()}')
        return response.json()

    def delete_secondary_signing_certificate(self, application_id):
        '''Delete secondary signing certificate for an application'''

        url = f'{self.api_gateway_url}/applications/{application_id}/secondary-signing-certificate'

        self.ensure_authenticated()
        response = ApsRequest.delete(url, headers=self.headers)
        LOGGER.debug(f'Delete secondary signing certificate response: {response.json()}')
        return response.json()

    def set_mapping_file(self, build_id, file):
        '''Set mapping for a build'''
        return self.multipart_upload(build_id, file, 'MAPPING_FILE')

    def set_aps_worker_build_environment(self, application_id, file):
        '''Set APS worker build environment for an application'''
        url = f'{self.api_gateway_url}/applications/{application_id}/build-environment'

        body = {}
        if file:
            with open(file, 'rb') as file_handle:
                body['environment'] = json.load(file_handle)
        self.ensure_authenticated()
        response = ApsRequest.put(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Set APS worker build environment response: {response.json()}')
        return response.json()

    def get_aps_worker_build_environment(self, application_id):
        '''Get APS worker build environment for an application'''
        url = f'{self.api_gateway_url}/applications/{application_id}/build-environment'

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers)
        LOGGER.debug(f'Get APS worker build environment response: {response.json()}')
        return response.json()

    def delete_aps_worker_build_environment(self, application_id):
        '''Delete APS worker build environment for an application'''

        url = f'{self.api_gateway_url}/applications/{application_id}/build-environment'

        self.ensure_authenticated()
        response = ApsRequest.delete(url, headers=self.headers)
        LOGGER.debug(f'Delete APS worker build environment response: {response.json()}')
        return response.json()

    def set_build_aps_worker_build_environment(self, build_id, file):
        '''Set APS worker build environment for a build'''
        url = f'{self.api_gateway_url}/builds/{build_id}/build-environment'

        body = {}
        if file:
            with open(file, 'rb') as file_handle:
                body['environment'] = json.load(file_handle)
        self.ensure_authenticated()
        response = ApsRequest.put(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Set build APS worker build environment response: {response.json()}')
        return response.json()

    def get_build_aps_worker_build_environment(self, build_id):
        '''Get APS worker build environment for a build'''
        url = f'{self.api_gateway_url}/builds/{build_id}/build-environment'

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers)
        LOGGER.debug(f'Get build APS worker build environment response: {response.json()}')
        return response.json()

    def delete_build_aps_worker_build_environment(self, build_id):
        '''Delete APS worker build environment for a build'''
        url = f'{self.api_gateway_url}/builds/{build_id}/build-environment'

        self.ensure_authenticated()
        response = ApsRequest.delete(url, headers=self.headers)
        LOGGER.debug(f'Delete build APS worker build environment response: {response.json()}')
        return response.json()

    def set_certificate_pinning_configuration(self, application_id, file):
        '''Set certificate pinning configuration for an application'''
        url = f'{self.api_gateway_url}/applications/{application_id}/certificate-pinning-configuration'

        body = {}
        if file:
            with open(file, 'rb') as file_handle:
                body['configuration'] = json.load(file_handle)
        self.ensure_authenticated()
        response = ApsRequest.put(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Set certificate pinning configuration response: {response.json()}')
        return response.json()

    def get_certificate_pinning_configuration(self, application_id):
        '''Get certificate pinning configuration for an application'''
        url = f'{self.api_gateway_url}/applications/{application_id}/certificate-pinning-configuration'

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers)
        LOGGER.debug(f'Get certificate pinning configuration response: {response.json()}')
        return response.json()

    def delete_certificate_pinning_configuration(self, application_id):
        '''Delete certificate pinning configuration for an application'''

        url = f'{self.api_gateway_url}/applications/{application_id}/certificate-pinning-configuration'

        self.ensure_authenticated()
        response = ApsRequest.delete(url, headers=self.headers)
        LOGGER.debug(f'Delete certificate pinning configuration response: {response.json()}')
        return response.json()

    def set_build_certificate_pinning_configuration(self, build_id, file):
        '''Set certificate pinning configuration for a build'''
        url = f'{self.api_gateway_url}/builds/{build_id}/certificate-pinning-configuration'

        body = {}
        if file:
            with open(file, 'rb') as file_handle:
                body['configuration'] = json.load(file_handle)
        self.ensure_authenticated()
        response = ApsRequest.put(url, headers=self.headers, data=json.dumps(body))
        LOGGER.debug(f'Set build certificate pinning configuration response: {response.json()}')
        return response.json()

    def get_build_certificate_pinning_configuration(self, build_id):
        '''Get certificate pinning configuration for a build'''
        url = f'{self.api_gateway_url}/builds/{build_id}/certificate-pinning-configuration'

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers)
        LOGGER.debug(f'Get build certificate pinning configuration response: {response.json()}')
        return response.json()

    def delete_build_certificate_pinning_configuration(self, build_id):
        '''Delete certificate pinning configuration for a build'''
        url = f'{self.api_gateway_url}/builds/{build_id}/certificate-pinning-configuration'

        self.ensure_authenticated()
        response = ApsRequest.delete(url, headers=self.headers)
        LOGGER.debug(f'Delete build certificate pinning configuration response: {response.json()}')
        return response.json()

    def get_sail_config(self, os_type, version):
        '''Get SAIL configuration'''
        url = f'{self.api_gateway_url}/sail_config'

        params = {}
        params['os'] = os_type
        if version:
            params['version'] = version

        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers, params=params)
        config = response.json()
        LOGGER.debug('Get SAIL configuration')
        return config

    def get_version(self):
        '''Get version'''
        url = f'{self.api_gateway_url}/version'
        self.ensure_authenticated()
        response = ApsRequest.get(url, headers=self.headers)
        return response.json()
