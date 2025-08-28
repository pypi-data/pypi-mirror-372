# Copyright (c) 2025. Verimatrix. All Rights Reserved.
# All information in this file is Verimatrix Confidential and Proprietary.
'''Helper utilities'''
import base64
import plistlib
import logging
import os
import shutil

from zipfile import is_zipfile, ZipFile
from pyaxmlparser import APK

from .aps_requests import ApsRequest
from .aps_exceptions import ApsException

LOGGER = logging.getLogger(__name__)

class ApsUtils:

    ALLOWED_SUFFIXES = {'.apk', '.aab', '.xcarchive.zip'}

    def authenticate_api_key(self, url, api_key):
        '''Authentication using an API Key. Returns a token (with expiration) that can be used as a HTTP authorization header'''
        LOGGER.info('Authenticating with provided API key')

        response = ApsRequest.post(url, json={'apiKey': api_key})
        resp = response.json()

        if 'token' not in resp:
            LOGGER.error('Failed to authenticate, please check API key')
            raise ApsException('Failed to authenticate, please check API key')
        
        return f'Bearer {resp["token"]}', resp["expirationTime"]

    def get_os(self, file):
        '''Deduce the OS based on the file extension'''
        if file.endswith(('.apk', '.aab')):
            return 'android'
        if file.endswith('.xcarchive.zip'):
            return 'ios'
        raise ApsException('Unsupported file suffix (must be .apk, .aab, or .xcarchive.zip)')

    def extract_file_data_from_zip(self, zipfile, file):
        '''Unzip a particular file from a zip archive'''
        try:
            filepath = zipfile.extract(file)
            with open(filepath, 'rb') as file_handle:
                data = base64.b64encode(file_handle.read()).decode('utf-8')
            os.remove(filepath)
            return data
        except Exception as e:
            LOGGER.error(f'Failed to extract file from zip: {e}')
            raise ApsException(f'Failed to extract {file} from zip')

    def extract_version_info(self, file):
        '''Extract application information from the input file to be protected'''
        if not any(file.endswith(suffix) for suffix in self.ALLOWED_SUFFIXES):
            LOGGER.critical('Input file must be .apk, .aab, or zipped .xcarchive')
            raise ApsException('Error: Unsupported file type')

        if not is_zipfile(file):
            LOGGER.critical('Input file is not a valid zip archive')
            raise ApsException('Error: File must be in zip format')

        version_info = {}

        with ZipFile(file) as zipfile:
            if file.endswith('.apk'):
                version_info['androidManifest'] = self.extract_file_data_from_zip(zipfile, 'AndroidManifest.xml')
            elif file.endswith('.aab'):
                version_info['androidManifestProtobuf'] = self.extract_file_data_from_zip(zipfile, 'base/manifest/AndroidManifest.xml')
            else:
                dirname = next((os.path.dirname(name) for name in zipfile.namelist() if not name.startswith('.')), None)

                for name in zipfile.namelist():
                    if '.app/Info.plist' in name and name.count('.app/') == 1:
                        version_info['iosBinaryPlist'] = self.extract_file_data_from_zip(zipfile, name)
                    elif dirname and name == f'{dirname}/Info.plist':
                        version_info['iosXmlPlist'] = self.extract_file_data_from_zip(zipfile, name)

                if dirname:
                    shutil.rmtree(dirname)

        return version_info

    def extract_package_id(self, file):
        '''Extract application package ID from binary file'''
        try:
            if file.endswith('.aab'):
                LOGGER.error('Cannot extract package ID from .aab files')
                return None

            version_info = self.extract_version_info(file)

            if 'androidManifest' in version_info:
                return APK(file).package
            elif 'iosXmlPlist' in version_info:
                plist = plistlib.loads(base64.b64decode(version_info['iosXmlPlist']))
                return plist['ApplicationProperties']['CFBundleIdentifier']
            elif 'iosBinaryPlist' in version_info:
                plist = plistlib.loads(base64.b64decode(version_info['iosBinaryPlist']))
                return plist['CFBundleIdentifier'].replace('"', '')

            raise ApsException('Unsupported file type')
        except Exception as e:
            LOGGER.error(f'Failed to extract application package ID: {e}')
            raise ApsException(f'Error extracting package ID: {e}')
