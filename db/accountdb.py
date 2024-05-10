import peewee
import datetime
from logger_config import logger
from db.pool import database
from entity.account_status import AccountStatus


# 定义模型类
class BaseModel(peewee.Model):
    class Meta:
        database = database


class Source:
    RUN_WAY = "RUN_WAY"
    PIKA = "PIKA"


class Account(BaseModel):
    id = peewee.AutoField(primary_key=True)
    account_no = peewee.CharField(max_length=255, unique=True)
    source = peewee.CharField(choices=[(Source.RUN_WAY, Source.RUN_WAY), (Source.PIKA, Source.PIKA)], null=False)
    password = peewee.CharField(max_length=255)
    job_num = peewee.IntegerField(default=4)
    balance = peewee.IntegerField(default=0)
    status = peewee.IntegerField(choices=[(status.value, status.name) for status in AccountStatus],
                                 default=AccountStatus.NORMAL)
    reason = peewee.CharField(max_length=255, default='')
    create_time = peewee.IntegerField(default=int(datetime.datetime.now().timestamp()))
    update_time = peewee.IntegerField(default=int(datetime.datetime.now().timestamp()))


# 检查模型类与数据库表结构的差异，并更新数据库表
def sync_table_structure():
    try:
        with database.atomic():
            # 检查 Account 表是否存在，不存在则创建
            if not Account.table_exists():
                Account.create_table()
                print("Table 'Account' created successfully.")

            # 检查字段是否在表中存在，不存在则添加
            fields_in_model = set(Account._meta.fields.keys())
            columns_in_table = database.get_columns('Account')

            column_names_in_table = [column.name for column in columns_in_table]

            fields_to_add = fields_in_model - set(column_names_in_table)
            for field_name in fields_to_add:
                field = Account._meta.fields[field_name]

                # 构造添加列的 SQL 语句并执行
                query = f"ALTER TABLE Account ADD COLUMN {field.name} {get_column_definition(field)}"
                database.execute_sql(query)

                print(f"Field '{field.name}' added to table 'Account'.")

            # 打印同步完成信息
            print("Table 'Account' structure synchronized successfully.")
    except peewee.OperationalError as e:
        print(f"Error occurred while synchronizing table structure: {e}")


# 获取字段的定义
def get_column_definition(field):
    if isinstance(field, peewee.CharField):
        return "VARCHAR(255)"  # 假设最大长度为 255
    elif isinstance(field, peewee.IntegerField):
        return "INTEGER"
    else:
        raise ValueError(f"Unsupported field type: {type(field)}")


# 创建表
def create_tables():
    with database:
        database.create_tables([Account])


# 检查是否已创建表的标志
def is_table_created():
    return Account.table_exists()


class AccountMapper:
    # 批量插入任务对象（仅插入不存在于数据库中的账号）
    def bulk_insert_tasks(self, accounts):
        accounts_to_insert = []
        for account in accounts:
            if not self.account_exists(account['id']):
                accounts_to_insert.append(account)
        if accounts_to_insert:
            with database.atomic():
                Account.insert_many(accounts_to_insert).execute()

    @staticmethod
    # 检查是否已经存在于数据库中
    def account_exists(_id):
        with database:
            return Account.select().where(Account.id == _id).exists()

    @staticmethod
    def get(_id):
        return Account.select().where(Account.id == _id).first()

    # 设置余额
    def set_balance(self, _id, account_status: int = None, reason: str = None, balance: int = None, count: int = None):
        account = self.get(_id)
        if account is None:
            return
        if account_status is not None:
            account.status = account_status
        if count is not None:
            account.count = count
        if reason is not None:
            account.reason = reason
        if balance is not None:
            account.balance = balance
        account.save()

    @staticmethod
    def get_random_normal_account(source):
        # 随机选择一个status为正常的账号
        return Account.select().where((Account.status == AccountStatus.NORMAL) & (Account.source == source)).order_by(
            peewee.fn.Random()).first()

    @staticmethod
    def get_by_account_no(source, _account_no):
        return Account.select().where((Account.source == source) & (Account.account_no == _account_no)).first()
