# This is a template config file for b2g emulator unittest testing
import platform
import os

HG_SHARE_BASE_DIR = "/builds/hg-shared"

if platform.system().lower() == 'darwin':
    xre_url = "http://tooltool.pvt.build.mozilla.org/build/sha512/ce54c2f5abb8b8bae67b129e1218e3c3fe46ed965992987b991d5b401e47db07a894da203978a710ea5498321c3b3d39538db2bca7db230c326af6ff060d7c98"
else:
    xre_url = "http://tooltool.pvt.build.mozilla.org/build/sha512/64b655694963a05b9cf8ac7f2e7480898e6613714c9bedafc3236ef633ce76e726585d0a76dbe4b428b5142ce85bebe877b70b5daaecf073e592cb505690839f"

config = {
    # mozharness script options
    "xre_url": xre_url,

    # mozharness configuration
    "tooltool_servers": ["http://tooltool.pvt.build.mozilla.org/build/"],

    "vcs_share_base": HG_SHARE_BASE_DIR,
    "exes": {
        'python': '/tools/buildbot/bin/python',
        'virtualenv': ['/tools/buildbot/bin/python', '/tools/misc-python/virtualenv.py'],
        'tooltool.py': "/tools/tooltool.py",
    },

    "find_links": [
        "http://pypi.pvt.build.mozilla.org/pub",
        "http://pypi.pub.build.mozilla.org/pub",
    ],
    "pip_index": False,

    "buildbot_json_path": "buildprops.json",

    "default_actions": [
        'clobber',
        'read-buildbot-config',
        'pull',
        'download-and-extract',
        'create-virtualenv',
        'install',
        'run-tests',
    ],
    "default_blob_upload_servers": [
        "https://blobupload.elasticbeanstalk.com",
    ],
    "blob_uploader_auth_file": os.path.join(os.getcwd(), "oauth.txt"),
    "vcs_output_timeout": 1760,
}
