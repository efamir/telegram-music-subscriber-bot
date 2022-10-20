import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('music_sub.db')
    cur = base.cursor()
    if base:
        print("Data base connected OK!")
    create_table_com = '''CREATE TABLE IF NOT EXISTS
    SubsAndAdmins (
        UserId INT NOT NULL,
        ChannelId INT NOT NULL,
        AdminOrSub BOOLEAN NOT NULL
    );
    '''
    base.execute(create_table_com)
    base.commit()


def truncate():
    cur.execute("DELETE FROM SubsAndAdmins")
    base.commit()


async def check_channel(channel_id: int):
    return bool(cur.execute("SELECT * FROM SubsAndAdmins WHERE ChannelId=?", (channel_id, )).fetchall())


async def sql_add(user_id: int, channel_id: int, admin_or_sub: bool):
    if not cur.execute("SELECT * FROM SubsAndAdmins WHERE UserId=? and ChannelId=? and AdminOrSub=?",
                       (user_id, channel_id, admin_or_sub)).fetchall():
        add_com = '''
        INSERT INTO SubsAndAdmins
        VALUES(?, ?, ?);
        '''
        cur.execute(add_com, (user_id, channel_id, admin_or_sub))
        base.commit()
        return True
    else:
        return False


async def read_channels_subs(channel_id: int):
    read_subs_com = '''
    SELECT UserId FROM SubsAndAdmins
    WHERE AdminOrSub = 0 and ChannelId = ?;
    '''
    return cur.execute(read_subs_com, (channel_id, )).fetchall()


async def unsub(channel_id: int, user_id: int):
    com = '''
    DELETE FROM SubsAndAdmins WHERE ChannelId = ? AND UserID = ? AND AdminOrSub = 0;
    '''
    cur.execute(com, (channel_id, user_id))
    base.commit()


async def check_if_admin(user_id: int):
    return cur.execute(
        "SELECT ChannelId FROM SubsAndAdmins WHERE UserId = ? AND AdminOrSub = 1;", (user_id, )).fetchall()
