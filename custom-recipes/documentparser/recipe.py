# Code for custom code recipe documentparser (imported from a Python recipe)

# To finish creating your custom recipe from your original PySpark recipe, you need to:
#  - Declare the input and output roles in recipe.json
#  - Replace the dataset names by roles access in your code
#  - Declare, if any, the params of your custom recipe in recipe.json
#  - Replace the hardcoded params values by acccess to the configuration map

# See sample code below for how to do that.
# The code of your original recipe is included afterwards for convenience.
# Please also see the "recipe.json" file for more information.

# import the classes for accessing DSS objects from the recipe
import dataiku
# Import the helpers for custom recipes
from dataiku.customrecipe import get_input_names_for_role
from dataiku.customrecipe import get_output_names_for_role
from dataiku.customrecipe import get_recipe_config
from upstgaedocumentparser.utils.recipes_io_utils import get_input_output

# Inputs and outputs are defined by roles. In the recipe's I/O tab, the user can associate one
# or more dataset to each input and output role.
# Roles need to be defined in recipe.json, in the inputRoles and outputRoles fields.

# The configuration consists of the parameters set up by the user in the recipe Settings tab.

# Parameters must be added to the recipe.json file so that DSS can prompt the user for values in
# the Settings tab of the recipe. The field "params" holds a list of all the params for wich the
# user will be prompted for values.
api_key = get_recipe_config()['api_key']['api_key']
api_option = get_recipe_config().get('api_option', '{}')
timeout = int(get_recipe_config().get('timeout', 60))
# The configuration is simply a map of parameters, and retrieving the value of one of them is simply:

# For optional parameters, you should provide a default value in case the parameter is not present:

# Note about typing:
# The configuration of the recipe is passed through a JSON object
# As such, INT parameters of the recipe are received in the get_recipe_config() dict as a Python float.
# If you absolutely require a Python int, use int(get_recipe_config()["my_int_param"])


#############################
# Your original recipe
#############################

import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
import requests
import json
import time
import os
from pathlib import Path

images, results = get_input_output('folder', 'folder')
paths = images.get_path()+images.list_paths_in_partition()[0]

def get_relative_path(file_path, main_folder):
    path = Path(file_path)
    parts = path.parts
    try:
        idx = parts.index(main_folder)
        after_main = parts[idx+1:]
        # 서브폴더 없어도, 깊은 폴더도 자동 처리
        result = Path(*after_main)
        return str(result)
    except ValueError:
        return ''  # 메인폴더 못 찾으면 빈 값

SUPPORTED_EXTENSIONS = (
    '.jpg', '.jpeg',  # JPEG
    '.png',           # PNG
    '.bmp',           # BMP
    '.tif', '.tiff',  # TIFF
    '.pdf',           # PDF
    '.heic',          # HEIC
    '.docx',          # DOCX
    '.pptx',          # PPTX
    '.xlsx'           # XLSX
)

def save_ocr_result_with_retry(
    file_path,
    url,
    headers,
    output_file_path,
    max_retries=5,
    base_sleep_time=10
):
    """
    단일 파일에 대해 OCR API 호출 -> 결과 JSON 저장 과정을 수행하는 함수.
    429(too_many_requests) 에러가 발생하면
    일정 시간 대기 후 재시도합니다.

    Parameters
    ----------
    file_path : str
        OCR을 진행할 이미지 파일 경로
    url : str
        OCR API 엔드포인트 URL
    headers : dict
        OCR API에 필요한 헤더 정보 (e.g. {"Authorization": "Bearer ..."})
    output_file_path : str
        OCR 결과를 저장할 JSON 파일 경로
    max_retries : int, optional
        429 에러 발생 시 재시도할 최대 횟수
    base_sleep_time : int, optional
        재시도 시도 간 기본 대기 시간(초). 매 재시도 시 배수로 증가 가능.
    """
    # 재시도 횟수
    retry_count = 0

    while True:
        with open(file_path, "rb") as file:
            files = {"document": file}
            response = requests.post(url, headers=headers, files=files)

        # 응답 상태코드 확인
        if response.status_code == 429:  # Too Many Requests
            retry_count += 1
            if retry_count > max_retries:
                # print(f"[ERROR] 재시도 횟수 초과 (파일: {file_path})")
                return  # 혹은 raise Exception 등을 통해 에러 처리

            # 응답에 지정된 대기 시간이 있으면 쓰는 게 가장 좋음(예: response.headers["Retry-After"])
            # 없으면 base_sleep_time의 배수만큼 대기
            wait_time = base_sleep_time * retry_count
            # print(f"[WARNING] 429 Too Many Requests. {wait_time}초 후 재시도합니다. (재시도 {retry_count}/{max_retries})")
            time.sleep(wait_time)
            continue
        else:
            # JSON 파싱
            try:
                ocr_data = response.json()
            except json.JSONDecodeError:
                print(f"[ERROR] JSON 디코딩 실패 (파일: {file_path})")
                return

            # OCR API에서 에러 메시지가 왔는지 확인
            error_info = ocr_data.get("error", {})
            error_type = error_info.get("type", "")
            error_code = error_info.get("code", "")

            if error_type == "too_many_requests" or error_code == "too_many_requests":
                # 이 경우도 429와 동일하게 처리(대기 후 재시도)
                retry_count += 1
                if retry_count > max_retries:
                    # print(f"[ERROR] 재시도 횟수 초과 (파일: {file_path})")
                    return
                wait_time = base_sleep_time * retry_count
                # print(f"[WARNING] too_many_requests 에러. {wait_time}초 후 재시도합니다. (재시도 {retry_count}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                # 정상 응답(혹은 다른 에러지만 429는 아님)이면 JSON 저장
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                with open(output_file_path, "w", encoding="utf-8") as f:
                    json.dump(ocr_data, f, ensure_ascii=False, indent=4)
                print("[INFO] OCR 결과 저장 완료:", output_file_path)
                return


def process_ocr_in_folder(root_ocr_img, root_ocr_json, url, headers, max_retries=5, base_sleep_time=10):
    """
    지정된 폴더 내 이미지 파일에 대하여 OCR을 진행하고,
    결과를 JSON으로 저장하는 함수입니다.
    429 에러가 발생할 경우 일정 시간 대기 후 재시도합니다.

    Parameters
    ----------
    root_ocr_img : str
        OCR 대상 이미지가 있는 폴더 경로
    root_ocr_json : str
        OCR 결과 JSON을 저장할 폴더 경로
    url : str
        OCR API 엔드포인트 URL
    headers : dict
        OCR API에 필요한 헤더 정보
    max_retries : int, optional
        429 에러 발생 시 재시도할 최대 횟수
    base_sleep_time : int, optional
        재시도 시도 간 기본 대기 시간(초). 매 재시도 시 배수로 증가 가능.
    """
    # 폴더 내 파일 순회
    
    for files in images.list_paths_in_partition():
        # 이미지인지 확인
        paths = images.get_path()+files
        main_folder = images.get_id()
        
        filename = get_relative_path(paths, main_folder)
        if filename.lower().endswith(SUPPORTED_EXTENSIONS):
            file_path = os.path.join(root_ocr_img, filename)
            #print(file_path)
            base_name = os.path.splitext(filename)[0]
            print(base_name)
            output_file_path = os.path.join(root_ocr_json, f"{base_name}.json")
            #print(root_ocr_json)
            #print(output_file_path)

            print(f"[INFO] Processing: {file_path}")
            #print(f"[INFO] Processing: {output_file_path}")

            # OCR 결과 저장 (429 대응 재시도 포함)
            save_ocr_result_with_retry(
                file_path=file_path,
                url=url,
                headers=headers,
                output_file_path=output_file_path,
                max_retries=max_retries,
                base_sleep_time=base_sleep_time
            )
    print("End")

root_ocr_img = images.get_path()
root_ocr_json = results.get_path()

url = "https://api.upstage.ai/v1/document-ai/ocr"
headers = {"Authorization": f"Bearer {api_key}"}

process_ocr_in_folder(
    root_ocr_img=root_ocr_img,
    root_ocr_json=root_ocr_json,
    url=url,
    headers=headers,
    max_retries=5,        # 재시도 최대 5회
    base_sleep_time=10    # 기본 대기 시간 10초 (재시도 시 2배씩 증가)
)