

import os
import sys
import tempfile
import logging
from pathlib import Path
from github import Github, GitReleaseAsset
from poly_hammer_utils.addon.packager import get_dict_from_python_file, zip_addon
import requests

logger = logging.getLogger(__name__)

class AddonRelease:
    def __init__(
            self, 
            github_token: str | None = None, 
            repo: str | None = None
        ):
        self._github_token = github_token or os.environ['GH_PAT']
        self.client = Github(login_or_token=self._github_token)
        self.repo = self.client.get_repo(repo or os.environ['GITHUB_REPO'])


    def get_previous_releases(self) -> list[str]:
        """
        Gets the previous releases.

        Returns:
            list[str]: A list of the previous addon releases.
        """
        return [release.tag_name for release in self.repo.get_releases()]
    
    def get_releases_attachments(self, tag: str) -> tuple[str, list[GitReleaseAsset.GitReleaseAsset]]:
        """
        Gets the release attachments. That match the tag.

        Args:
            tag (str): The tag to get the attachments for.

        Returns:
            tuple[str, list[GitReleaseAsset.GitReleaseAsset]]: The tag name and the attachments.
        """
        for release in self.repo.get_releases():
            if tag.lower() == 'latest':
                return release.tag_name, [asset for asset in release.get_assets()]

            if release.tag_name == tag:
                return release.tag_name, [asset for asset in release.get_assets()]
            
        return '', []
    

    def delete_release(self, tag_name: str):
        """
        Deletes a release.
        
        Args:
            tag_name (str): The tag name of the release to delete.
        """
        for release in self.repo.get_releases():
            if release.tag_name == tag_name:
                release.delete_release()
                logger.debug(f'Deleted release "{tag_name}"')

    def trigger_core_build_workflow(
            self, 
            repo: str,
            title: str,
            message: str,
            tag: str,
        ):
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._github_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        payload = {
            "event_type": "dispatch-event",
            "client_payload": {
                "title": title,
                "message": message,
                "tag": tag
            }
        }

        response = requests.post(
            f"https://api.github.com/repos/{repo}/dispatches",
            headers=headers,
            json=payload
        )

        if response.status_code == 204:
            logger.info("Successfully triggered the core build workflow.")
        else:
            raise RuntimeError(f"Failed to trigger the core build workflow: {response.status_code} {response.text}")
        

    def trigger_docs_build_workflow(self, repo: str):
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self._github_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        payload = {
            "event_type": "dispatch-event",
            "client_payload": {}
        }

        response = requests.post(
            f"https://api.github.com/repos/{repo}/dispatches",
            headers=headers,
            json=payload
        )

        if response.status_code == 204:
            logger.info("Successfully triggered the docs build workflow.")
        else:
            raise RuntimeError(f"Failed to trigger the docs build workflow: {response.status_code} {response.text}")


    def create_release(
            self, 
            addon_folder: Path, 
            requirements: Path | None = None,
            trigger_core_build: str | None = None,
            ignore_patterns: tuple[str] = ()
        ):
        """
        Creates a release for the addon if it doesn't exist already.

        Args:
            addon_folder (Path): The path to the addon folder.
            
            requirements (Path): The path to the requirements file. If None, 
            no extra packages from the addon will be installed.

            trigger_core_build (str): The repo name with the addon's core modules. If specified, the core modules build workflow will be triggered.

            ignore_patterns (tuple[str]): The patterns to ignore when zipping the addon.
        """
        # ignore zipping the core modules if the core build is triggered
        ignore_patterns = list(ignore_patterns)
        if trigger_core_build:
            ignore_patterns.append('core')

        addon_zip = zip_addon(
            addon_folder_path=addon_folder,
            output_folder=Path(tempfile.gettempdir()) / 'poly_hammer' / 'releases',
            requirements=requirements,
            ignore_patterns=ignore_patterns
        )

        previous_releases = self.get_previous_releases()
        bl_info = get_dict_from_python_file(
            python_file=addon_folder / '__init__.py',
            dict_name='bl_info'
        )
        title = bl_info['name']
        tag_name = '.'.join([str(i) for i in bl_info['version']])
        message = ''
        release_notes_path = addon_folder / 'release_notes.md'
        if release_notes_path.exists():
            with open(release_notes_path) as release_notes:
                message = release_notes.read()

        if tag_name not in previous_releases:
            logger.info(f'Creating release "{title}"')
            release = self.repo.create_git_release(
                name=title,
                message=message,
                tag=tag_name
            )

            logger.info(f'Uploading "{addon_zip}"')
            release.upload_asset(
                path=str(addon_zip),
                name=addon_zip.name,
                content_type='application/zip'
            )
        elif os.environ.get('FORCE_RELEASE'):
            logger.warning(f'Release "{tag_name}" already exists!')
            self.delete_release(tag_name=tag_name)

            logger.info(f'Overwriting release "{title}"')
            release = self.repo.create_git_release(
                name=title,
                message=message,
                tag=tag_name
            )

            logger.info(f'Uploading "{addon_zip}"')
            release.upload_asset(
                path=str(addon_zip),
                name=addon_zip.name,
                content_type='application/zip'
            )
        
        logger.info('Successfully released!')

        if trigger_core_build:
            logger.info('Triggering core release...')
            self.trigger_core_build_workflow(
                repo=trigger_core_build,
                title=title,
                message=message,
                tag=tag_name
            )
            logger.info('Triggered core release.')

    def create_core_release(
            self,
            file_path: Path,
            title: str,
            message: str,
            tag: str,
        ):
        previous_releases = self.get_previous_releases()
        if tag not in previous_releases:
            logger.info(f'Creating release "{title}"')
            release = self.repo.create_git_release(
                name=title,
                message=message,
                tag=tag
            )

            logger.info(f'Uploading "{file_path}"')
            release.upload_asset(
                path=str(file_path),
                name=file_path.name,
                content_type='application/zip'
            )
        else:            
            release = self.repo.get_release(tag)
            # Remove the asset if it already exists
            for asset in release.get_assets():
                if asset.name == file_path.name:
                    asset.delete_asset()
                    logger.info(f'Deleting existing attachment "{asset.name}" on release "{tag}"')

            logger.info(f'Uploading additional attachment "{file_path}" to release "{tag}"')
            release.upload_asset(
                path=str(file_path),
                name=file_path.name,
                content_type='application/zip'
            )
        
        logger.info('Successfully released core!')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    if sys.argv[-1] == 'core':
        AddonRelease().create_core_release(
            file_path=Path(os.environ['CORE_FILE']),
            title=os.environ['CORE_TITLE'],
            message=os.environ['CORE_MESSAGE'],
            tag=os.environ['CORE_TAG']
        )
    elif sys.argv[-1] == 'docs':
        AddonRelease().trigger_docs_build_workflow(repo=os.environ['DOCS_REPO'])
    else:
        AddonRelease().create_release(
            addon_folder=Path(os.environ['ADDON_FOLDER']),
            trigger_core_build=os.environ.get('CORE_REPO'),
            ignore_patterns=[i for i in os.environ.get('IGNORE_PATTERNS', '').split(',') if i]
        )