# Google Drive Read-only File Downloader

This project is neither affiliated with nor endorsed by Google or Google Drive.

This project uses a combination of [gpsoauth](https://github.com/simon-weber/gpsoauth) for authentication and a very basic reverse engineering of the internal API used by the Google Drive app on Android to download read-only files, identical to how they were when uploaded, from Google Drive. This API is intentionally less restricted as it is used by the app on Android in a somewhat trusted environment where a document or image is downloaded to the cache folder of the app for temporary viewing, and that folder is inaccessible to non-rooted users.

The 2 API calls exposed here work with all normal file types, and download them as they are. This means that using this project, you can't download or stream a specific format of a video - which is something you should use [yt-dlp](https://github.com/yt-dlp/yt-dlp) for.

Using this project to download files or circumvent a deliberate lock where you would not be allowed by law to do so is **STRICTLY PROHIBITED AND CAN RESULT IN SERIOUS PUNIHSMENT. I DO NOT CONDONE SUCH ACTIONS.**

This project spawned from me having to archive read-only PDF files for legal purposes.
