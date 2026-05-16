import enum

class MarketPlace(str, enum.Enum):
    wildberries = 'wildberries'
    ozon = 'ozon'

class TaskStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class TaskType(str, enum.Enum):
    fetch_cards = "fetch_cards"
    track_positions = "track_positions"