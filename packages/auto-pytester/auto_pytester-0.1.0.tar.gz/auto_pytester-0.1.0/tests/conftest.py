import pytest
import pymysql
import pymongo

@pytest.fixture
def project_name():
    return "Radius Pytest Plugins"

@pytest.fixture
def temp_file(tmp_path):       
    f = tmp_path / "data.txt"
    f.write_text("hello")
    yield f      


@pytest.fixture(scope="function")
def db_session():
    # SQLAlchemy 示例
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session                 
    session.rollback()            # 每个测试结束回滚，保证隔离！
    session.close()


@pytest.fixture(params=["redis", "memcached"])
def cache_client(request):
    if request.param == "redis":
        import redis
        r = redis.Redis()
        yield r
        r.flushdb()
    else:
        import pymemcache.client
        c = pymemcache.client.Client(("127.0.0.1", 11211))
        yield c
        c.flush_all()