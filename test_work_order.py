import unittest
from work_order import WorkOrder, photo_request

class PhotoAccessTest(unittest.TestCase):
    def test_completed_order_allows_assigned_technician(self) -> None:
        order = WorkOrder("WO-1", "completed", "tech-7", "WO-1/photo.jpg")
        self.assertEqual(photo_request(order, "tech-7"), "WO-1/photo.jpg")
        self.assertIsNone(photo_request(order, "tech-9"))

    def test_dispatched_order_does_not_issue_photo(self) -> None:
        order = WorkOrder("WO-2", "dispatched", "tech-7", "WO-2/photo.jpg")
        self.assertIsNone(photo_request(order, "tech-7"))

if __name__ == "__main__":
    unittest.main()
