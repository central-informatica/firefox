def commit_and_refresh(db, obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
