# from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, func
# from sqlalchemy.orm import relationship


# from utils.database import Base
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

# class User(Base):
#     __tablename__ = "user"

#     id = Column(String, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     password = Column(String)
#     password_hashed = Column(String)
#     first_name = Column(String(40), default="")
#     last_name = Column(String(40), default="")
#     token = Column(String, default="")
#     update_datetime = Column(DateTime())
#     create_datetime = Column(DateTime())
#     is_active = Column(Boolean, default=True)

#     domain_id = Column(String, ForeignKey("domain.id"))
#     domain = relationship("Domain", back_populates="user")
    
#     items = relationship("Item", back_populates="owner")


# class Item(Base):
#     __tablename__ = "item"

#     id = Column(String, primary_key=True, index=True)
#     title = Column(String)
#     description = Column(String)
#     code = Column(String, index=True)
#     flag1 = Column(String)
#     flag2 = Column(String)

#     owner_id = Column(String, ForeignKey("user.id"))
#     owner = relationship("User", back_populates="items")


# class Domain(Base):
#     __tablename__ = "domain"

#     id = Column(String, primary_key=True, index=True)
#     name = Column(String)
#     title = Column(String)
#     description = Column(String)
#     update_datetime = Column(DateTime())
#     update_by = Column(String)
#     create_datetime = Column(DateTime())
#     create_by = Column(String)

#     user = relationship("User", back_populates="domain")




# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object
# many-to-many
# class Association(Base):
#     __tablename__ = 'association'
#     left_id = Column(Integer, ForeignKey('left.id'), primary_key=True)
#     right_id = Column(Integer, ForeignKey('right.id'), primary_key=True)
#     extra_data = Column(String(50))
#     child = relationship("Child")

# class Parent(Base):
#     __tablename__ = 'left'
#     id = Column(Integer, primary_key=True)
#     children = relationship("Association")

# class Child(Base):
#     __tablename__ = 'right'
#     id = Column(Integer, primary_key=True)