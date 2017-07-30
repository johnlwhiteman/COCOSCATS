from Plugin.Interface import Interface
import argparse
import httplib2
import os
import re
import sys
from urllib.parse import urlparse
from apiclient.discovery import build_from_document
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from Core.File import File
from Core.Text import Text
# Reference: https://developers.google.com/youtube/v3/guides/authenticatio
# https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

class YouTubeGoogleCaptionsApiCode(object):

    def __init__(self):
        self.__ARGS = None
        self.__ARGS_PARSER = None
        self.__ASSETS_DIR = None
        self.__DOWNLOAD_PATH = None
        self.__CLIENT_API_CAPTIONS_FILE = None
        self.__CLIENT_SECRETS_FILE = None
        self.__CLIENT_OAUTH2_ACCESS_TOKEN_FILE = None
        self.__YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
        self.__YOUTUBE_API_SERVICE_NAME = "youtube"
        self.__YOUTUBE_API_VERSION = "v3"
        self.__MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:
{0}
with information from the APIs Console
https://console.developers.google.com

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""".format(self.__CLIENT_SECRETS_FILE)

    def initialize(self, params):
        self.__PARAMS = params
        self.__ASSETS_DIR ="{0}/__YouTube".format(
            os.path.dirname(os.path.realpath(__file__)).replace('\\', '/'))
        self.__CLIENT_API_CAPTIONS_FILE = "{0}/youtube-v3-api-captions.json".format(self.__ASSETS_DIR)
        if not os.path.isfile(self.__CLIENT_API_CAPTIONS_FILE):
            raise Exception(
                "Missing YouTube API file file. Download it from Google and put in this path: {0}".format(self.__CLIENT_API_CAPTIONS_FILE))
        self.__DOWNLOADED_PATH = "{0}/downloadedCaptions.srt".format(self.__ASSETS_DIR)
        self.__TRANSLATED_PATH = "{0}/translatedCaptions.txt".format(self.__ASSETS_DIR)
        self.__CLIENT_SECRETS_FILE = "{0}/client_secrets.json".format(self.__PARAMS["VaultPath"])
        if not os.path.isfile(self.__CLIENT_SECRETS_FILE):
            raise Exception(
                "Missing client_secrets.json file. Download it from your Google account and put under the Cocoscat's Vault directory" )
        self.__CLIENT_OAUTH2_ACCESS_TOKEN_FILE = "{0}/client_secrets_oauth2.json".format(self.__PARAMS["VaultPath"])
        parser = argparse.ArgumentParser(parents=[argparser])
        parser.add_argument("--videoid",
            help="ID for video for which the caption track will be uploaded.", default=self.__PARAMS["URL"]["VideoID"])
        parser.add_argument("--name", help="Caption track name", default=self.__PARAMS["CaptionName"])
        parser.add_argument("--file", help="Captions track file to upload")
        parser.add_argument("--language", help="Caption track language", default=self.__PARAMS["L1"])
        parser.add_argument("--captionid", help="Required; ID of the caption track to be processed")
        parser.add_argument("--action", help="Action", default="all")

        # Using argsparse is dumb idea in a class but it's not my design. I need to include main client's args
        # until I can figure a better way here to do this here
        parser.add_argument("-c", "--cfg", metavar="'cfg'", type=str, default="cfg.json",
                             help="JSON configuration file")
        parser.add_argument("-C", "--cli", action="store_true",
                            help="Run command line interface")
        parser.add_argument("-W", "--web", action="store_true",
                             help="Run web interface")

        self.__ARGS_PARSER = parser

        if Text.isTrue(self.__PARAMS["RefreshOAUTH2AccessToken"]):
            File.delete(self.__CLIENT_OAUTH2_ACCESS_TOKEN_FILE)

        if not File.exists(self.__CLIENT_OAUTH2_ACCESS_TOKEN_FILE):
            self.generateOAUTH2AccessToken()

    def delete_caption(self, youtube, caption_id):
        youtube.captions().delete(
            id=caption_id
        ).execute()
        print ("caption track '%s' deleted succesfully" % (caption_id))

    def deleteOAUTH2AccessToken(self):
        if os.path.isfile(self.__CLIENT_OAUTH2_ACCESS_TOKEN_FILE):
            print("TODO: DELETE IT SIR")

    def download_caption(self):
        args = self.__ARGS_PARSER.parse_known_args(
                ["--action", "upload", "--file", self.__DOWNLOADED_PATH])
        youtube = self.get_authenticated_service(args)
        subtitle = youtube.captions().download(
            id=self.__PARAMS["CaptionID"],
            tfmt=self.__PARAMS["Format"]
        ).execute()
        return subtitle

    def downloadCaption(self):
        captions = self.download_caption().decode()
        File.setContent(self.__DOWNLOADED_PATH, captions)
        return captions

    def generateOAUTH2AccessToken(self):
        args = self.__ARGS_PARSER.parse_args()
        youtube = self.get_authenticated_service(args)


    def get_authenticated_service(self, args):
        flow = flow_from_clientsecrets(self.__CLIENT_SECRETS_FILE,
                                       scope=self.__YOUTUBE_READ_WRITE_SSL_SCOPE,
                                       message=self.__MISSING_CLIENT_SECRETS_MESSAGE)
        storage = Storage(self.__CLIENT_OAUTH2_ACCESS_TOKEN_FILE)
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage, args)
        with open(self.__CLIENT_API_CAPTIONS_FILE, "r", encoding="utf-8") as f:
            doc = f.read()
            return build_from_document(doc, http=credentials.authorize(httplib2.Http()))

    def getDownloadedCaptions(self):
        return File.getContent(self.__DOWNLOADED_PATH)

    def list_captions(self):
        args = self.__ARGS_PARSER.parse_known_args()
        youtube = self.get_authenticated_service(args)
        results = youtube.captions().list(
            part="snippet",
            videoId=self.__PARAMS["URL"]["VideoID"]
        ).execute()
        for item in results["items"]:
            id = item["id"]
            name = item["snippet"]["name"]
            language = item["snippet"]["language"]
            print ("Caption track '%s(%s)' in '%s' language." % (name, id, language))
        return results["items"]

    def saveTranslatedCaptions(self, content):
        File.setContent(self.__TRANSLATED_PATH, content)

    def setCaptionID(self, captionID=None):
        if captionID is not None:
            self.__PARAMS["CaptionID"] = captionID
            return self.__PARAMS["CaptionID"]
        captions = self.list_captions()
        for caption in captions:
            if caption["snippet"]["language"].lower() == self.__PARAMS["L1"].lower():
                self.__PARAMS["CaptionID"] = caption["id"]
                print("Found Caption ID: {0}".format(caption["id"]))
                return self.__PARAMS["CaptionID"]
        raise Exception("Can't find Caption ID based on video and language")

    def update_caption(self):
        args = self.__ARGS_PARSER.parse_known_args(
                ["--action", "update", "--file", self.__TRANSLATED_PATH])
        youtube = self.get_authenticated_service(args)
        update_result = youtube.captions().update(
            part="snippet",
            body=dict(
            id=self.__PARAMS["CaptionID"],
            snippet=dict(
                isDraft=self.__PARAMS["IsDraft"]
            )
            ),
            media_body=self.__TRANSLATED_PATH
        ).execute()
        name = update_result["snippet"]["name"]
        isDraft = update_result["snippet"]["isDraft"]
        #print("Updated caption track '%s' draft status to be: '%s'" % (name, isDraft))
        #if file:
        #    print("and updated the track with the new uploaded file.")

    def updateCaption(self):
        self.update_caption()
        print("Captions update completed: {0}".format(self.__PARAMS["URL"]["URL"]))

    def upload_caption(self, youtube, video_id, language, name, file):
        insert_result = youtube.captions().insert(
            part="snippet",
            body=dict(
            snippet=dict(
                videoId=self.__PARAMS["VideoID"],
                language=self.__PARAMS["L1"],
                name=self.__PARAMS["CaptionName"],
                isDraft=True
            )
            ),
            media_body=file
        ).execute()
        id = insert_result["id"]
        name = insert_result["snippet"]["name"]
        language = insert_result["snippet"]["language"]
        status = insert_result["snippet"]["status"]
        print ("Uploaded caption track '%s(%s) in '%s' language, '%s' status." % (name,
            id, language, status))


class YouTube(Interface):

    def __init__(self, cfg, pluginParams, workflowPluginParams, frameworkParams):
        super(YouTube, self).__init__(cfg, pluginParams, workflowPluginParams, frameworkParams)

    def __parseContentForInputSRT(self, rawContent):
        content = []
        newLineTracker = 0
        for token in rawContent.split("\n"):
            token = token.strip()
            if re.search("-->", token) or token.isdigit() or Text.isNothing(token):
                if newLineTracker < 1:
                    content.append("")
                newLineTracker += 1
            else:
                content.append(token)
                newLineTracker = 0
        content = "\n".join(content).strip()
        return content

    def __parseContentForOutputSRT(self, rawContent):
        tc = self.getTranslatorContentAsJson()
        counters = []
        markers = []
        subtitles = []
        for token in rawContent.split("\n"):
            token = token.strip()
            if Text.isNothing(token):
                continue
            if token.isdigit():
                counters.append(token)
            elif re.search("-->", token):
                markers.append(token)
        tc["L1L2"] = tc["L1L2"].strip()
        subtitle = ""
        for token in tc["L1L2"].split("\n"):
            token = token.strip()
            if Text.isNothing(token):
                subtitles.append(subtitle)
                subtitle = ""
            else:
                subtitle = "{0}\n{1}".format(subtitle, token)
        subtitles.append(subtitle)
        content = ""
        for i in range(0, len(counters)):
            content = "{0}\n{1}\n{2}{3}\n".format(
                content, counters[i], markers[i], subtitles[i])
        content = content.lstrip()
        return content

    def __parseURL(self, url):
        u = urlparse(url)
        subtitleFormat = "srt"
        videoID = None
        L1 = "en"
        api = "http://www.youtube.com/api/timedtext?format={0}&lang={1}&v=".format(
            subtitleFormat, L1)
        if not re.search(u.netloc, "www.youtube.com|www.youtu.be",  re.IGNORECASE):
            return None
        if re.search("/watch?", u.path, re.IGNORECASE):
            videoID = re.split("&", u.query)[0][2:]
        elif re.match("/embed/", u.path, re.IGNORECASE):
            videoID = re.split("/embed/", u.path, re.IGNORECASE)[1:][0]
        elif re.search("youtu.be", u.netloc, re.IGNORECASE):
            videoID = u.path[1:]
        elif re.match("/v/", u.path, re.IGNORECASE):
            videoID = re.split("/v/", u.path, re.IGNORECASE)[1]
        if videoID is None:
            return None
        return {"API": """{0}{1}""".format(api, videoID),
                "VideoID": videoID,
                "ParsedURL": u,
                "URL": url}

    def __runSetup(self):
        sourceURL = self.getWorkflowSource()
        url = self.__parseURL(sourceURL)
        if url is None:
            Exception(
                "Invalid YouTube URL. Unable to ascertain Video ID: {0}".format(sourceURL))
        params = {
            "CaptionID": None,
            "CaptionName": self.getPluginParamValue("CaptionName"),
            "Format": self.getPluginParamValue("Format"),
            "IsDraft": Text.isTrue(self.getPluginParamValue("IsDraft")),
            "L1": self.getPluginParamValue("L1"),
            "RefreshOAUTH2AccessToken": self.getPluginParamValue("RefreshOAUTH2AccessToken").lower() == "true",
            "VaultPath": self.getVaultPath(),
            "URL": url,
        }
        api = YouTubeGoogleCaptionsApiCode()
        api.initialize(params)
        api.setCaptionID()
        return api

    def runInputUsingLocalFile(self):
        target = self.getWorkflowSource()
        rawContent = File.getContent(target)
        return self.__parseContentForInputSRT(rawContent)

    def runInputUsingRemoteFile(self):
        api = self.__runSetup()
        rawContent = api.downloadCaption()
        content = self.__parseContentForInputSRT(rawContent)
        self.setInputContent(content)
        del(api)
        return content

    def runOutputUsingLocalFile(self):
        rawContent = File.getContent(self.getWorkflowSource())
        content = self.__parseContentForOutputSRT(rawContent)
        self.setOutputContent(content)
        return content

    def runOutputUsingRemoteFile(self):
        api = self.__runSetup()
        rawContent = api.getDownloadedCaptions()
        content = self.__parseContentForOutputSRT(rawContent)
        api.saveTranslatedCaptions(content)
        api.updateCaption()
        self.setOutputContent(content)
        return content