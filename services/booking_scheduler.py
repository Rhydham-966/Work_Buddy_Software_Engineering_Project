# services/booking_scheduler.py

class BookingScheduler:
    def __init__(self):
        # { professional_id: [time_slots] }
        self.booked_slots = {}

    def is_available(self, professional_id, time_slot):
        slots = self.booked_slots.get(professional_id, [])
        return time_slot not in slots

    def book_slot(self, professional_id, time_slot):
        if professional_id not in self.booked_slots:
            self.booked_slots[professional_id] = []

        self.booked_slots[professional_id].append(time_slot)