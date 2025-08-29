# Add common quartzbio classes and methods our namespace here so that
# inside the ipython shell users don't have run imports
import quartzbio  # noqa
from quartzbio import login  # noqa
from quartzbio import Annotator  # noqa
from quartzbio import Application  # noqa
from quartzbio import Beacon  # noqa
from quartzbio import BeaconSet  # noqa
from quartzbio import BatchQuery  # noqa
from quartzbio import Dataset  # noqa
from quartzbio import DatasetCommit  # noqa
from quartzbio import DatasetExport  # noqa
from quartzbio import DatasetField  # noqa
from quartzbio import DatasetImport  # noqa
from quartzbio import DatasetMigration  # noqa
from quartzbio import DatasetTemplate  # noqa
from quartzbio import Expression  # noqa
from quartzbio import Filter  # noqa
from quartzbio import GenomicFilter  # noqa
from quartzbio import Manifest  # noqa
from quartzbio import Object  # noqa
from quartzbio import Query  # noqa
from quartzbio import QuartzBioClient  # noqa
from quartzbio import QuartzBioError  # noqa
from quartzbio import User  # noqa
from quartzbio import Vault  # noqa
from quartzbio import Task  # noqa
from quartzbio import VaultSyncTask  # noqa
from quartzbio import ObjectCopyTask  # noqa
from quartzbio import SavedQuery  # noqa
from quartzbio import DatasetRestoreTask  # noqa
from quartzbio import DatasetSnapshotTask  # noqa
from quartzbio import GlobalSearch  # noqa
from quartzbio import Group  # noqa
from quartzbio.utils.printing import pager  # noqa

# Add some convenience functions to the interactive shell
from quartzbio.cli.auth import logout  # noqa
from quartzbio.cli.auth import whoami  # noqa
from quartzbio.cli.auth import get_credentials  # noqa

whoami()
