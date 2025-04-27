# achievements.py
# Achievements definitions embedded directly in Python (no JSON file needed)
import os

class AchievementManager:
    def __init__(self,
                 save_path=None):
        # Define all achievements inline as Python list of dicts
        self.achdefs = [
            {
                'id': 'first_row',
                'name': 'İlk Satırı Temizle',
                'description': 'Oyun sırasında ilk satırını temizledin!',
                'event': 'row_cleared',
                'threshold': 1
            },
            {
                'id': 'merge_2048',
                'name': '2048 Birleştirdin',
                'description': '2048 bloğunu oluşturmayı başardın!',
                'event': 'tile_merged',
                'threshold': 2048
            },
            {
                'id': 'score_1000',
                'name': 'Puan 1000',
                'description': 'Puanın 1000’e ulaştı!',
                'event': 'score_update',
                'threshold': 1000
            }
        ]
        # Determine save file path for unlocked achievements
        base = os.path.dirname(__file__)
        self.save_path = save_path or os.path.join(base, 'achieved.json')

        # Load previously unlocked achievements, if any
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                import json
                self.unlocked = set(json.load(f))
        except Exception:
            self.unlocked = set()

        # Progress tracker for non-score events
        self.progress = {}

    def report_event(self, event, value=1):
        for ach in self.achdefs:
            aid = ach['id']
            if aid in self.unlocked or ach['event'] != event:
                continue

            if event == 'score_update':
                # Directly check current score against threshold
                if value >= ach['threshold']:
                    self._unlock(ach)
            else:
                # Accumulate for row_cleared and tile_merged
                self.progress.setdefault(aid, 0)
                self.progress[aid] += value
                if self.progress[aid] >= ach['threshold']:
                    self._unlock(ach)

    def _unlock(self, ach):
        self.unlocked.add(ach['id'])
        self._notify(ach)
        self._save()

    def _notify(self, ach):
        # Simple console notification; can be replaced with stddraw toast
        print(f"🏆 Achievement Unlocked: {ach['name']}")

    def _save(self):
        try:
            import json
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(list(self.unlocked), f, ensure_ascii=False, indent=2)
        except Exception:
            pass
