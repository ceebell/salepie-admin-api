from pydantic import BaseModel, constr

# อนุญาต a-z, A-Z, 0-9, space, และอักขระพิเศษ ?!*%
alpNumStr = constr(pattern=r'^[a-zA-Z0-9\s]+$')

# อนุญาต a-z, A-Z, 0-9, space, และอักขระพิเศษ ?!*%
alpNumSpeStr = constr(pattern=r'^[a-zA-Z0-9\s\?\!\*\%]+$')

# อนุญาต a-z, A-Z, 0-9, emojis (U+1F600-U+1F64F), space
emojiAlnumStr = constr(pattern=r'^[\w\d\s\U0001F600-\U0001F64F]+$')  # 😂🥰😎