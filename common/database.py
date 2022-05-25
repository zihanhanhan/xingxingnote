from sqlalchemy import MetaData


def dbconnect():
    from main import db
    dbsession = db.session  #
    DBase = db.Model  # 声明模型
    metadata = MetaData(bind=db.engine)
    # MetaData 是一个容器对象，它将描述的数据库（或多个数据库）的许多不同功能放在一起。
    return (dbsession, metadata, DBase)
