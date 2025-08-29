from typing import List, Optional, Tuple, IO

from square_commons.api_utils import make_request_json_output
from square_database_structure.square.authentication.enums import RecoveryMethodEnum

from square_authentication_helper.pydantic_models import TokenType


class SquareAuthenticationHelper:
    def __init__(
        self,
        param_int_square_authentication_port: int = 10011,
        param_str_square_authentication_ip: str = "localhost",
        param_str_square_authentication_protocol: str = "http",
    ):
        try:
            self.global_str_square_authentication_url_base = (
                f"{param_str_square_authentication_protocol}://"
                f"{param_str_square_authentication_ip}:{param_int_square_authentication_port}"
            )
        except Exception:
            raise

    def _make_request(
        self,
        method,
        endpoint,
        json=None,
        data=None,
        params=None,
        headers=None,
        files=None,
    ):
        try:
            return make_request_json_output(
                method=method,
                base_url=self.global_str_square_authentication_url_base,
                endpoint=endpoint,
                json=json,
                data=data,
                params=params,
                headers=headers,
                files=files,
            )

        except Exception:
            raise

    def register_username_v0(
        self,
        username: str,
        password: str,
        app_id: Optional[int] = None,
    ):
        try:
            endpoint = "register_username/v0"
            data = {
                "username": username,
                "password": password,
                "app_id": app_id,
            }
            return self._make_request(method="POST", endpoint=endpoint, json=data)
        except Exception:
            raise

    def login_username_v0(
        self,
        username: str,
        password: str,
        app_id: int,
        assign_app_id_if_missing: bool = False,
    ):
        try:
            endpoint = "login_username/v0"
            data = {
                "username": username,
                "password": password,
                "app_id": app_id,
                "assign_app_id_if_missing": assign_app_id_if_missing,
            }
            return self._make_request(method="POST", endpoint=endpoint, json=data)
        except Exception:
            raise

    def generate_access_token_v0(
        self,
        refresh_token: str,
    ):
        try:
            endpoint = "generate_access_token/v0"
            headers = {
                "refresh_token": refresh_token,
            }
            return self._make_request(method="GET", endpoint=endpoint, headers=headers)
        except Exception:
            raise

    def logout_v0(
        self,
        refresh_token: str,
    ):
        try:
            endpoint = "logout/v0"
            headers = {
                "refresh_token": refresh_token,
            }
            return self._make_request(
                method="DELETE", endpoint=endpoint, headers=headers
            )
        except Exception:
            raise

    def logout_apps_v0(
        self,
        access_token: str,
        app_ids: List[int],
    ):
        try:
            endpoint = "logout/apps/v0"
            headers = {
                "access_token": access_token,
            }
            body = {
                "app_ids": app_ids,
            }
            return self._make_request(
                method="POST", endpoint=endpoint, headers=headers, json=body
            )
        except Exception:
            raise

    def logout_all_v0(
        self,
        access_token: str,
    ):
        try:
            endpoint = "logout/all/v0"
            headers = {
                "access_token": access_token,
            }
            return self._make_request(
                method="DELETE", endpoint=endpoint, headers=headers
            )
        except Exception:
            raise

    def get_user_details_v0(
        self,
        access_token: str,
    ):
        try:
            endpoint = "get_user_details/v0"
            headers = {
                "access_token": access_token,
            }
            return self._make_request(
                method="GET",
                endpoint=endpoint,
                headers=headers,
            )
        except Exception:
            raise

    def update_user_app_ids_v0(
        self,
        access_token: str,
        app_ids_to_add: List[int],
        app_ids_to_remove: List[int],
    ):
        try:
            endpoint = "update_user_app_ids/v0"
            headers = {
                "access_token": access_token,
            }
            payload = {
                "app_ids_to_add": app_ids_to_add,
                "app_ids_to_remove": app_ids_to_remove,
            }
            return self._make_request(
                method="PATCH", endpoint=endpoint, headers=headers, json=payload
            )
        except Exception:
            raise

    def update_username_v0(
        self,
        new_username: str,
        access_token: str,
    ):
        try:
            endpoint = "update_username/v0"
            params = {
                "new_username": new_username,
            }
            headers = {
                "access_token": access_token,
            }
            return self._make_request(
                method="PATCH", endpoint=endpoint, params=params, headers=headers
            )
        except Exception:
            raise

    def delete_user_v0(
        self,
        password: str,
        access_token: str,
    ):
        try:
            endpoint = "delete_user/v0"
            data = {
                "password": password,
            }
            headers = {
                "access_token": access_token,
            }
            return self._make_request(
                method="POST", endpoint=endpoint, json=data, headers=headers
            )
        except Exception:
            raise

    def update_password_v0(
        self,
        old_password: str,
        new_password: str,
        access_token: str,
        logout_other_sessions: bool = False,
        preserve_session_refresh_token: str = None,
    ):
        try:
            endpoint = "update_password/v0"
            data = {
                "old_password": old_password,
                "new_password": new_password,
                "logout_other_sessions": logout_other_sessions,
                "preserve_session_refresh_token": preserve_session_refresh_token,
            }
            headers = {
                "access_token": access_token,
            }
            return self._make_request(
                method="PATCH", endpoint=endpoint, json=data, headers=headers
            )
        except Exception:
            raise

    def validate_and_get_payload_from_token_v0(
        self, token: str, token_type: TokenType, app_id: int
    ):
        try:
            endpoint = "validate_and_get_payload_from_token/v0"
            params = {"token_type": token_type.value, "app_id": app_id}
            headers = {
                "token": token,
            }
            return self._make_request(
                method="GET", endpoint=endpoint, headers=headers, params=params
            )
        except Exception:
            raise

    def update_profile_photo_v0(
        self, access_token: str, profile_photo: Tuple[str, IO, str] | None
    ):
        try:
            endpoint = "update_profile_photo/v0"

            headers = {
                "access_token": access_token,
            }
            if profile_photo:
                files = {
                    "profile_photo": profile_photo,
                }
            else:
                files = None
            return self._make_request(
                method="PATCH", endpoint=endpoint, headers=headers, files=files
            )
        except Exception:
            raise

    def update_user_recovery_methods_v0(
        self,
        access_token: str,
        recovery_methods_to_add: List[RecoveryMethodEnum] = None,
        recovery_methods_to_remove: List[RecoveryMethodEnum] = None,
    ):
        if recovery_methods_to_add is None:
            recovery_methods_to_add = []
        if recovery_methods_to_remove is None:
            recovery_methods_to_remove = []
        try:
            endpoint = "update_user_recovery_methods/v0"

            headers = {
                "access_token": access_token,
            }
            # convert to json serializable format
            recovery_methods_to_add_formatted = [
                method.value for method in recovery_methods_to_add
            ]
            recovery_methods_to_remove_formatted = [
                method.value for method in recovery_methods_to_remove
            ]
            json = {
                "recovery_methods_to_add": recovery_methods_to_add_formatted,
                "recovery_methods_to_remove": recovery_methods_to_remove_formatted,
            }
            return self._make_request(
                method="PATCH", endpoint=endpoint, headers=headers, json=json
            )
        except Exception:
            raise

    def generate_account_backup_codes_v0(
        self,
        access_token: str,
    ):
        try:
            endpoint = "generate_account_backup_codes/v0"

            headers = {
                "access_token": access_token,
            }
            return self._make_request(method="POST", endpoint=endpoint, headers=headers)
        except Exception:
            raise

    def reset_password_and_login_using_backup_code_v0(
        self,
        backup_code: str,
        username: str,
        new_password: str,
        app_id: int,
        logout_other_sessions: bool = False,
    ):
        try:
            endpoint = "reset_password_and_login_using_backup_code/v0"

            json = {
                "backup_code": backup_code,
                "username": username,
                "new_password": new_password,
                "app_id": app_id,
                "logout_other_sessions": logout_other_sessions,
            }
            return self._make_request(method="POST", endpoint=endpoint, json=json)
        except Exception:
            raise

    def send_reset_password_email_v0(
        self,
        username: str,
    ):
        try:
            endpoint = "send_reset_password_email/v0"

            json = {
                "username": username,
            }
            return self._make_request(method="POST", endpoint=endpoint, json=json)
        except Exception:
            raise

    def validate_email_verification_code_v0(
        self,
        access_token: str,
        verification_code: str,
    ):
        try:
            endpoint = "validate_email_verification_code/v0"
            headers = {
                "access_token": access_token,
            }
            json = {
                "verification_code": verification_code,
            }
            return self._make_request(
                method="POST", endpoint=endpoint, json=json, headers=headers
            )
        except Exception:
            raise

    def send_verification_email_v0(
        self,
        access_token: str,
    ):
        try:
            endpoint = "send_verification_email/v0"
            headers = {
                "access_token": access_token,
            }

            return self._make_request(method="POST", endpoint=endpoint, headers=headers)
        except Exception:
            raise

    def update_profile_details_v0(
        self,
        access_token: str,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        phone_number_country_code: str = None,
        phone_number: str = None,
    ):
        try:
            endpoint = "update_profile_details/v0"
            headers = {
                "access_token": access_token,
            }
            json = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone_number_country_code": phone_number_country_code,
                "phone_number": phone_number,
            }

            return self._make_request(
                method="PATCH", endpoint=endpoint, json=json, headers=headers
            )
        except Exception:
            raise

    def reset_password_and_login_using_reset_email_code_v0(
        self,
        reset_email_code: str,
        username: str,
        new_password: str,
        app_id: int,
        logout_other_sessions: bool = False,
    ):
        try:
            endpoint = "reset_password_and_login_using_reset_email_code/v0"

            json = {
                "reset_email_code": reset_email_code,
                "username": username,
                "new_password": new_password,
                "app_id": app_id,
                "logout_other_sessions": logout_other_sessions,
            }

            return self._make_request(
                method="POST",
                endpoint=endpoint,
                json=json,
            )
        except Exception:
            raise

    def register_login_google_v0(
        self,
        google_id: str,
        app_id: int = None,
        assign_app_id_if_missing: bool = False,
    ):
        try:
            endpoint = "register_login_google/v0"

            json = {
                "google_id": google_id,
                "app_id": app_id,
                "assign_app_id_if_missing": assign_app_id_if_missing,
            }

            return self._make_request(
                method="POST",
                endpoint=endpoint,
                json=json,
            )
        except Exception:
            raise
