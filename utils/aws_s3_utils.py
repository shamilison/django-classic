from __future__ import absolute_import, unicode_literals

import logging
import os

from django.core.files.storage import default_storage

from django_classic.logging.classic_logger import ClassicLogger

logging.setLoggerClass(ClassicLogger)
logger = logging.getLogger(__name__)


class AwsS3ActionUtils(object):

    @classmethod
    def upload_to_s3(cls, file_name, aws_file_path, local_file_path):
        if not default_storage.exists(aws_file_path):
            _file = open(local_file_path, 'rb')
            default_storage.save(aws_file_path, _file)
            logger.debug(f'Uploaded to s3: {file_name}', extra={})
            return True
        else:
            logger.debug(f'Upload ignored as file already exists in s3: {file_name}', extra={})
            return False

    @classmethod
    def delete_from_s3(cls, file_key):
        if default_storage.exists(file_key):
            default_storage.delete(file_key)
            logger.debug(f'Deleted from s3: {file_key}', extra={})
            return True
        else:
            logger.debug(f'Delete ignored as file not exists in s3: {file_key}', extra={})
            return False
