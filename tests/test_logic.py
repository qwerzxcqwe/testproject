import unittest
from models.workload import Workload, Credentials, MountPoint
from models.migration import Migration, MigrationTarget, CloudType
import os
from persistence import storage


class TestWorkload(unittest.TestCase):
    def setUp(self):
        self.cred = Credentials(username="admin", password="pass", domain="local")
        self.mounts = [MountPoint(name="C:\\", total_size=100), MountPoint(name="D:\\", total_size=200)]
        self.wl = Workload(ip="192.168.1.1", credentials=self.cred, storage=self.mounts)
        if os.path.exists("data"):
            for f in os.listdir("data"):
                os.remove(os.path.join("data", f))

    def test_workload_creation(self):
        self.assertEqual(self.wl.ip, "192.168.1.1")
        self.assertEqual(len(self.wl.storage), 2)

    def test_ip_immutability(self):
        with self.assertRaises(ValueError):
            self.wl.ip = "10.0.0.1"

    def test_storage_filtering(self):
        filtered = self.wl.clone_selected_mountpoints(["C:\\"])
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].name, "C:\\")

    def test_persistence(self):
        storage.save_workload(self.wl)
        loaded = storage.load_all_workloads()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].ip, "192.168.1.1")

    def test_migration_run(self):
        target_vm = Workload(ip="192.168.1.1", credentials=self.cred, storage=[])
        target = MigrationTarget(cloud_type=CloudType.aws, cloud_credentials=self.cred, target_vm=target_vm)
        migrate = Migration(selected_mount_points=["C:\\"], source=self.wl, target=target)
        migrate.run()
        self.assertEqual(migrate.state.value, "success")
        self.assertEqual(len(target.target_vm.storage), 1)
        self.assertEqual(target.target_vm.storage[0].name, "C:\\")

    def test_migration_without_C(self):
        target_vm = Workload(ip="192.168.1.1", credentials=self.cred, storage=[])
        target = MigrationTarget(cloud_type=CloudType.aws, cloud_credentials=self.cred, target_vm=target_vm)
        migrate = Migration(selected_mount_points=["D:\\"], source=self.wl, target=target)
        with self.assertRaises(PermissionError):
            migrate.run()

    def test_migration_delete(self):
        target_vm = Workload(ip="192.168.1.1", credentials=self.cred, storage=[])
        target = MigrationTarget(cloud_type=CloudType.vsphere, cloud_credentials=self.cred, target_vm=target_vm)
        migrate = Migration(selected_mount_points=["C:\\"], source=self.wl, target=target)
        storage.save_migration(migrate)

        storage.delete_migration(migrate)

        all_migs = storage.load_all_migrations()
        self.assertEqual(len(all_migs), 0)


if __name__ == "__main__":
    unittest.main()
