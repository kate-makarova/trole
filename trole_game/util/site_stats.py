from trole_game.models import SiteStatistics


class SiteStat:
    key = None
    value_field = None

    def get_stat(self):
        stat = SiteStatistics.objects.filter(key=self.key)
        if len(stat) == 0:
            return False
        return stat[0]

    def set(self, value):
        stat = self.get_stat()
        stat[self.value_field] = value
        stat.save()

class SiteStatInt(SiteStat):
    key = None
    value_field = 'int_field'

    def increment(self, value = 1):
        stat = self.get_stat()
        stat[self.value_field] += value
        stat.save()

    def decrement(self, value = 1):
        stat = self.get_stat()
        stat[self.value_field] -= value
        stat.save()

class SiteStatDateTime(SiteStat):
    key = None
    value_field = 'date_time_field'

class TotalUserCountStat(SiteStatInt):
    key = 'total_user_count'

class TotalGameCountStat(SiteStatInt):
    key = 'total_game_count'

class TotalCharacterCountStat(SiteStatInt):
    key = 'total_game_count'

class TotalEpisodeCountStat(SiteStatInt):
    key = 'total_game_count'

class TotalPostCountStat(SiteStatInt):
    key = 'total_game_count'

class OnlineIn24CountStat(SiteStatInt):
    key = 'online_in_24_count'

class LastPostPublished(SiteStatDateTime):
    key = 'last_post_published'