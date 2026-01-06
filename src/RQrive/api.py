from pathlib import Path
from threading import Thread
from time import time
import gpsoauth
import requests
import json


def auth(oauth_token: str) -> dict:
    email = ""
    android_id = "0123456"
    master_response = gpsoauth.exchange_token(email, oauth_token, android_id)
    return master_response


def access_token(master_token: dict) -> dict:
    a_token = {
        "email": master_token["Email"],
        "master_token": master_token["Token"],
        "android_id": "0123456",
        "token": None,
        "valid_until": None,
    }
    auth = gpsoauth.perform_oauth(
        a_token["email"],
        a_token["master_token"],
        a_token["android_id"],
        "oauth2:https://www.googleapis.com/auth/drive",
        app="com.google.android.apps.docs",
        client_sig="38918a453d07199354f8b19af05ec6562ced5788",
    )
    a_token["token"] = auth["Auth"]
    a_token["valid_until"] = auth["Expiry"]
    return a_token.copy()


def _refresh_token(access_token: dict) -> None:
    if int(access_token["valid_until"]) >= int(time()):
        auth = gpsoauth.perform_oauth(
            access_token["email"],
            access_token["master_token"],
            access_token["android_id"],
            "oauth2:https://www.googleapis.com/auth/drive",
            app="com.google.android.apps.docs",
            client_sig="38918a453d07199354f8b19af05ec6562ced5788",
        )
        access_token["token"] = auth["Auth"]
        access_token["valid_until"] = auth["Expiry"]


def get_file_info(access_token, file_id: str) -> dict:
    _refresh_token(access_token)
    uri = f"https://www.googleapis.com/drive/v2internal/files/{file_id}?supportsAllDrives=true&includePermissionsForView=published&allProperties=false&fields=publishingInfo%28published%29%2cmimeType%2cexportLinks%2cdownloadUrl%2ckind%2cfolderColorRgb%2csharedWithMeDate%2clastViewedByMeDate%2cpermissionsSummary%28visibility%28type%29%29%2ccontentRestrictions%2freadOnly%2cabuseIsAppealable%2cthumbnailVersion%2cheadRevisionId%2cmodifiedDate%2crecency%2cdriveId%2clabels%28starred%2cviewed%2crestricted%2ctrashed%29%2cparent%2fid%2ccreatedDate%2csubscribed%2calternateLink%2cid%2cversion%2cquotaBytesUsed%2cetag%2cdetectors%2cancestorHasAugmentedPermissions%2cfolderFeatures%2cspaces%2ccustomerId%2cabuseNoticeReason%2cworkspaceIds%2ctitle%2cshared%2chasAugmentedPermissions%2cparents%2fid%2cowners%28emailAddressFromAccount%2cid%2corganizationDisplayName%29%2ctrashedDate%2cresourceKey%2corganizationDisplayName%2copenWithLinks%2cdefaultOpenWithLink%2cfileSize%2chasLegacyBlobComments%2cexplicitlyTrashed%2creadersCanSeeComments%2clastModifyingUser%28id%2cemailAddressFromAccount%29%2ccapabilities%28canMoveItemWithinDrive%2ccanTrashChildren%2ccanRemoveChildren%2ccanReadCategoryMetadata%2ccanManageMembers%2ccanTrash%2ccanShare%2ccanAddMyDriveParent%2ccanListChildren%2ccanPrint%2ccanCopy%2ccanDeleteChildren%2ccanDelete%2ccanRename%2ccanModifyContent%2ccanRequestApproval%2ccanBlockOwner%2ccanCopyNonAuthoritative%2ccanReadDrive%2ccanMoveChildrenOutOfDrive%2ccanMoveItemOutOfDrive%2ccanDownload%2ccanShareChildFolders%2ccanChangePermissionExpiration%2ccanAddChildren%2ccanComment%2ccanAcceptOwnership%2ccanEdit%2ccanShareChildFiles%2ccanUntrash%2ccanManageVisitors%2ccanDownloadNonAuthoritative%2ccanChangeSecurityUpdateEnabled%2ccanReportSpamOrAbuse%2ccanMoveChildrenWithinDrive%29%2cactionItems%2cblockingDetectors%2cownedByMe%2cshortcutDetails%28targetResourceKey%2ctargetId%2ctargetMimeType%2ctargetLookupStatus%2ctargetFile%29%2cspamMetadata%28markedAsSpamDate%2cinSpamView%29%2cprimarySyncParentId%2cprimaryDomainName%2csharingUser%28emailAddressFromAccount%2cid%29%2cclientEncryptionDetails%28decryptionMetadata%29%2crecencyReason%2cmd5Checksum%2ccontainsUnsubscribedChildren%2capprovalMetadata%28approvalVersion%2capprovalSummaries%29%2chasThumbnail%2cmodifiedByMeDate%2cpassivelySubscribed&reportPermissionErrors=true&updateViewedDate=true&reason=1351&featureLabel=android-sync-native"
    headers = {"Authorization": "Bearer {}".format(access_token["token"])}
    response = requests.get(uri, headers=headers)
    return json.loads(str(response.content, "utf-8"))


class File:
    def __init__(self, access_token, file_id, file_name):
        _refresh_token(access_token)
        self.progress = 0
        self._access_token = access_token
        self._cancel = False
        self._file_id = file_id
        self._file_name = file_name
        self._download_thread = Thread(target=self._download, daemon=True)

    def download(self):
        self._cancel = False
        self._download_thread.start()
    
    def cancel(self):
        self._cancel = True

    def _download(self):
        uri = "https://www.googleapis.com/download/drive/v2internal/files/{}?alt=media".format(
            self._file_id
        )
        headers = {"Authorization": "Bearer {}".format(self._access_token["token"])}
        try:
            with requests.get(uri, headers=headers, stream=True) as response:
                response.raise_for_status()
                with open(self._file_name, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if self._cancel:
                            raise FileExistsError
                        self.progress += len(chunk)
                        file.write(chunk)
        except FileExistsError:
            file = Path(self._file_name)
            file.resolve().unlink()