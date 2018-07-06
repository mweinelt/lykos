import re
import random
from collections import Counter

from src.utilities import *
from src import users, channels, debuglog, errlog, plog
from src.functions import get_players, get_all_players
from src.decorators import cmd, event_listener
from src.containers import UserList, UserSet, UserDict, DefaultUserDict
from src.messages import messages
from src.events import Event

# Generated message keys used in this file:
# mystic_safe, mystic_wolfteam, mystic_win_stealer,
# mystic_night_num, mystic_day_num, mystic_info,
# mystic_simple, mystic_notify, wolf_mystic_simple, wolf_mystic_notify

def setup_variables(rolename, *, send_role, types):
    LAST_COUNT = UserDict() # type: Dict[users.User, Tuple[str, bool]]

    role = rolename.replace(" ", "_")

    @event_listener("transition_night_end")
    def on_transition_night_end(evt, var):
        role_cats_evt = Event("get_role_metadata", {})
        role_cats_evt.dispatch(var, "role_categories")
        pl = get_players()
        ctr = Counter()

        for p in pl:
            role = get_main_role(p)
            for t in role_cats_evt.data[role].intersection(types):
                ctr[t] += 1

        values = []
        plural = True
        for name in types:
            keyname = "mystic_" + name.replace(" ", "_")
            l = ctr[name]
            if l:
                if not values and l == 1:
                    plural = False
                values.append("\u0002{0}\u0002 {1}{2}".format(l, messages[keyname], "" if l == 1 else "s"))

        if len(values) > 2:
            value = " and ".join((", ".join(values[:-1]), values[-1]))
        else:
            value = " and ".join(values)
        msg = messages["mystic_info"].format("are" if plural else "is", value, " still", "")

        for mystic in get_all_players((rolename,)):
            LAST_COUNT[mystic] = (value, plural)
            if send_role:
                to_send = "{0}_{1}".format(role, ("simple" if mystic.prefers_simple() else "notify"))
                mystic.send(messages[to_send])
            mystic.send(msg)

    @event_listener("exchange_roles")
    def on_exchange_roles(evt, var, actor, target, actor_role, target_role):
        if actor_role == rolename and target_role != rolename:
            value, plural = LAST_COUNT.pop(actor)
            LAST_COUNT[target] = (value, plural)
            key = "were" if plural else "was"
            msg = messages["mystic_info"].format(key, value, "", messages["mystic_{0}_num".format(var.PHASE)])
            evt.data["target_messages"].append(msg)

        if target_role == rolename and actor_role != rolename:
            value, plural = LAST_COUNT.pop(target)
            LAST_COUNT[actor] = (value, plural)
            key = "were" if plural else "was"
            msg = messages["mystic_info"].format(key, value, "", messages["mystic_{0}_num".format(var.PHASE)])
            evt.data["actor_messages"].append(msg)

    @event_listener("reset")
    def on_reset(evt, var):
        LAST_COUNT.clear()

    @event_listener("myrole")
    def on_myrole(evt, var, user):
        if user in get_all_players((rolename,)):
            value, plural = LAST_COUNT[user]
            key = "were" if plural else "was"
            msg = messages["mystic_info"].format(key, value, "", messages["mystic_{0}_num".format(var.PHASE)])
            evt.data["messages"].append(mag)

    return LAST_COUNT

# vim: set sw=4 expandtab:
