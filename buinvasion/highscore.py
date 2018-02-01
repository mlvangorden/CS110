import sqlite3


class HighScore:

    def __init__(self, num):
        self.conn = sqlite3.connect("HighScore.db")
        self.table = "HighScore"
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM sqlite_master WHERE name = ? and type = ?", (self.table, "table"))
        result = self.cursor.fetchone()
        if (not result):
            self.cursor.execute("CREATE TABLE {tn} ({ri} {dt})".format(tn = self.table, ri = "Name", dt = "varchar"))
            self.cursor.execute("ALTER TABLE {tn} ADD COLUMN '{ri}' {dt}".format(tn = self.table, ri = "Score", dt = "int"))
        else:
            print("Table already exists")
        self.max_scores = num

    def addScore(self, name, score):
        self.cursor.execute("SELECT COUNT(*) FROM {tn}".format(tn = self.table))
        num = self.cursor.fetchone()
        if (num[0] < self.max_scores):
            self.cursor.execute("INSERT INTO {tn} VALUES(?, ?)".format(tn = self.table), (name, score))
        else:
            #finding min score
            self.cursor.execute("SELECT MIN(score) FROM {tn}".format(tn = self.table))
            minscore = self.cursor.fetchone()
            #check if the min score is less than currect score
            if (minscore[0] < score):
                #delete based on record name
                self.cursor.execute("DELETE FROM {tn} WHERE score = ?".format(tn = self.table), (minscore[0],))
                self.cursor.execute("INSERT INTO {tn} VALUES (?,?)".format(tn = self.table), (name, score))
            else:
                print("Sorry, {nm} didn't cut it.".format(nm = name))

    def checkHighScore(self, score):
        self.cursor.execute("SELECT COUNT(*) FROM {tn}".format(tn = self.table))
        num = self.cursor.fetchone()
        if (num[0] < self.max_scores):
            return True

        self.cursor.execute("SELECT MIN(score) FROM {tn}".format(tn = self.table))
        minscore = self.cursor.fetchone()
        if score > minscore[0]:
            return True

        else:
            return False

    def highScorers(self):
        self.cursor.execute("SELECT * FROM {tn} ORDER BY score DESC".format(tn = self.table))
        return self.cursor.fetchall()

    def closeConnection(self):
        self.conn.commit()
        self.cursor.close()

def test():
    hs = HighScore(5)
    hs.addScore("Matt", 50)
    hs.addScore("Richard", 75)
    hs.addScore("Nathan", 100)

    for s in hs.highScorers():
        print(s[0], s[1])
    hs.closeConnection()

#test()
