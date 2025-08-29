from .aws_utils import copy_s3_object
from config.env_config import env_config

import logging
log = logging.getLogger(__name__)



def copy_report_to_tableau_bucket(env_param, file_name, s3_key):
    s3_bucket = env_config[env_param]["feature-store-bucket"]
    s3_exp_bucket = env_config[env_param]["exposed-bucket"]
    s3_tableau_root_key = env_config[env_param]["exposed-send-to-tableau-path"]

    copy_source = {"Bucket": s3_bucket, "Key": s3_key}
    s3_exp_key = f"{s3_tableau_root_key}/{file_name}"

    log.info(f"Started file upload {file_name} to tableau bucket.")
    copy_s3_object(copy_source, s3_exp_bucket, s3_exp_key)
    log.info(f"Finished file upload {file_name} to tableau bucket.")

def copy_report_to_email_bucket(env_param, file_name, s3_key, prefix):
    s3_bucket = env_config[env_param]["feature-store-bucket"]
    s3_exp_bucket = env_config[env_param]["exposed-bucket"]
    s3_email_root_key = env_config[env_param]["exposed-send-to-email-path"]
    
    report_prefix = env_config[env_param][prefix]

    copy_source = {"Bucket": s3_bucket, "Key": s3_key}
    exp_file_name = f"{report_prefix}_{file_name}"
    s3_exp_key = f"{s3_email_root_key}/{exp_file_name}"

    log.info(f"Started file upload {exp_file_name} to email bucket.")
    copy_s3_object(copy_source, s3_exp_bucket, s3_exp_key)
    log.info(f"Finished file upload {exp_file_name} to email bucket.")

def copy_report_to_email_bucket_marketplace(env_param, file_name, s3_key):
    s3_bucket = env_config[env_param]["feature-store-bucket"]
    s3_exp_bucket = env_config[env_param]["exposed-bucket"]
    s3_email_root_key = env_config[env_param]["exposed-send-to-email-path"]
    report_prefix = env_config[env_param]["exposed-cod-report-prefix_compact"]

    copy_source = {"Bucket": s3_bucket, "Key": s3_key}
    exp_file_name = f"{report_prefix}_{file_name}"
    s3_exp_key = f"{s3_email_root_key}/{exp_file_name}"

    log.info(f"Started file upload {exp_file_name} to email bucket.")
    copy_s3_object(copy_source, s3_exp_bucket, s3_exp_key)
    log.info(f"Finished file upload {exp_file_name} to email bucket.")
