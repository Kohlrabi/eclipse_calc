equipment = {
        'ion': {'damage': 1, 'power': -1},
        'plasma': {'damage': 2, 'power': -2},
        'antimatter' : {'damage': 4, 'power': -3},
        'rocket' : {'damage':2, 'shots': 2, 'first_strike': True},
        'armor1' : {'armor': 1},
        'armor2' : {'armor': 2},
        'computer1' : {'aim': 1},
        'computer2' : {'aim': 2, 'power': -1, 'ini': 1},
        'computer3' : {'aim': 3, 'power': -2, 'ini': 2},
        'shield1' : {'shield': 1},
        'shield2' : {'shield': 2, 'power': -1},
        'engine1' : {'ini': 1, 'power': -1},
        'engine2' : {'ini': 2, 'power': -2},
        'engine3' : {'ini': 3, 'power': -3},
        'generator1' : {'power': 3},
        'generator2' : {'power': 6},
        'generator3' : {'power': 9},
    }

class ship():
    def __init__(self, n=1, validate=False, **kwargs):
        self.equip = {}
        self.my_ini = 0
        self.my_power = 0
        self.my_aim = 0

        for k, v in kwargs.items():
            if k in equipment:
                self.equip.update({k: v})
            else:
                if k == 'ini':
                    self.my_ini = v
                if k == 'power':
                    self.my_power = v
                if k == 'aim':
                    self.my_aim = v

        self.n = n
        if validate:
            self.validate()
   
    def _sum(self, typ):
        ret = 0
        for e,n in self.equip.items():
            try:
                ret += equipment[e][typ] * n
            except KeyError:
                pass
        return ret

    @property
    def ini(self):
        return self._sum('ini') + self.my_ini
        
    @property
    def shield(self):
        return self._sum('shield')
    
    @property
    def aim(self):
        return self._sum('aim') + self.my_aim
    
    @property
    def power(self):
        return self._sum('power') + self.my_power

    @property
    def armor(self):
        return self._sum('armor')

    @property
    def has_first_strike(self):
        for e in self.equip:
            if 'first_strike' in equipment[e]:
                return True
        return False

    @property
    def has_beam_weapons(self):
        if 'ion' in self.equip and self.equip['ion'] > 0:
            return True
        if 'plasma' in self.equip and self.equip['plasma'] > 0:
            return True
        if 'antimatter' in self.equip and self.equip['antimatter'] > 0:
            return True
        return False

    @property
    def has_weapons(self):
        if not self.has_first_strike and not self.has_beam_weapons:
            return False
        else:
            return True


    def validate(self):
        if self.power < 0:
            raise ValueError("Ship consumes too much power: %d"%self.power)

class interceptor(ship):
    def __init__(self, n=1, validate=False, default=False, **kwargs):
        if default:
            ship.__init__(self, n, validate, ini=2, ion=1, engine1=1, generator1=1)
        else:
            ship.__init__(self, n, validate, ini=2, **kwargs)

class cruiser(ship):
    def __init__(self, n=1, validate=False, default=False, **kwargs):
        if default:
            ship.__init__(self, n, validate, ini=1, ion=1, computer1=1, armor1=1, engine1=1, generator1=1)
        else:
            ship.__init__(self, n, validate, ini=1, **kwargs)

class dreadnought(ship):
    def __init__(self, n=1, validate=False, default=False, **kwargs):
        if default:
            ship.__init__(self, n, validate, ion=2, computer1=1, armor1=2, engine1=1, generator1=1)
        else:
            ship.__init__(self, n, validate, **kwargs)

class base(ship):
    def __init__(self, n=1, validate=False, default=False, **kwargs):
        if default:
            ship.__init__(self, n, validate, ini=4, ion=1, armor1=1)
        else:
            ship.__init__(self, n, validate, ini=4, **kwargs)

class ancient(ship):
    def __init__(self, n=1, validate=False, default=True, **kwargs):
        ship.__init__(self, n, validate, ini=2, ion=2, computer1=1, armor1=1)

class gc(ship):
    def __init__(self, n=1, validate=False, default=True, **kwargs):
        ship.__init__(self, n, validate, ion=4, computer1=1, armor1=7)

class fleet():
    def __init__(self):
        self.ships = []

    def add(self, ship):
        self.ships.append(ship)

    def __len__(self):
        return len(self.ships)

    def __iadd__(self, ship):
        self.ships.append(ship)
        return self


class battle():
    def __init__(self, attacker, defender):
        self.at = attacker
        self.de = defender
        self.at.nn = self.at.n
        self.de.nn = self.de.n

    def roll(self, n=1):
        import random

        ret = [random.randint(1,6) for i in range(n)]
        return ret

    def hits(self, n, aim=0, shield=0):
        rolls = self.roll(n)
        no_ones = [r for r in rolls if r != 1]
        no_sixes = [r + aim-shield for r in no_ones if r != 6]
        hits = len(no_ones) - len(no_sixes) + len([r for r in no_sixes if r >= 6])

        return hits

    def do_first_strikes(self, at, de):
        n = at.equip['rocket'] * equipment['rocket']['shots']
        dd = self.hits(n * at.n, at.aim, de.shield)
        for i in range(dd):
            de.damage += equipment['rocket']['damage']
            if de.damage > de.armor:
                de.n -= 1
                de.damage = 0

    def do_attack(self, at, de):
        try:
            n1 = at.equip['ion']
            dd1 = self.hits(n1 * at.n, at.aim, de.shield)
            for i in range(dd1):
                de.damage += equipment['ion']['damage']
                if de.damage > de.armor:
                    de.n -= 1
                    de.damage = 0
        except KeyError:
            pass

        try:
            n2 = at.equip['plasma']
            dd2 = self.hits(n2 * at.n, at.aim, de.shield)
            for i in range(dd2):
                de.damage += equipment['plasma']['damage']
                if de.damage > de.armor:
                    de.n -= 1
                    de.damage = 0
        except KeyError:
            pass


        try:
            n4 = at.equip['antimatter']
            dd4 = self.hits(n4 * at.n, at.aim, de.shield)
            for i in range(dd4):
                de.damage += equipment['antimatter']['damage']
                if de.damage > de.armor:
                    de.n -= 1
                    de.damage = 0
        except KeyError:
            pass
        

    def battle(self):

        self.at.n = self.at.nn
        self.de.n = self.de.nn

        self.at.damage = 0
        self.de.damage = 0

        ain = self.at.ini
        din = self.de.ini

        max_loop = 1000
      
        if ain > din:
            if self.at.has_first_strike:
                self.do_first_strikes(self.at, self.de)
                if self.de.n <= 0:
                    return self.at.n
            if self.de.has_first_strike:
                self.do_first_strikes(self.de, self.at)
                if self.at.n <= 0:
                    return -self.de.n

            if not self.at.has_beam_weapons and not self.de.has_beam_weapons:
                return -self.de.n

            for i in range(max_loop):
                self.do_attack(self.at, self.de)
                if self.de.n <= 0:
                    return self.at.n
                self.do_attack(self.de, self.at)
                if self.at.n <= 0:
                    return -self.de.n
            return -self.de.n

        if ain < din:
            if self.de.has_first_strike:
                self.do_first_strikes(self.de, self.at)
                if self.at.n <= 0:
                    return -1
            if self.at.has_first_strike:
                self.do_first_strikes(self.at, self.de)
                if self.de.n <= 0:
                    return 1

            if not self.at.has_weapons and not self.de.has_weapons:
                return -self.de.n

            for i in range(max_loop):
                self.do_attack(self.de, self.at)
                if self.at.n <= 0:
                    return -self.de.n
                self.do_attack(self.at, self.de)
                if self.at.n <= 0:
                    return self.at.n
            return -self.de.n

        if ain == din:
            self.de.nnn = self.de.n
            if self.at.has_first_strike:
                self.do_first_strikes(self.at, self.de)
            temp = self.de.n
            self.de.n = self.de.nnn
            if self.de.has_first_strike:
                self.do_first_strikes(self.de, self.at)
            self.de.n = temp

            if self.at.n <= 0:
                if self.de.n <= 0:
                    return 0
                else:
                    return -self.de.n
            if self.de.n <= 0:
                return self.at.n

            if not self.at.has_weapons and not self.de.has_weapons:
                return -self.de.n

            for i in range(max_loop):
                self.de.nnn = self.de.n
                self.do_attack(self.at, self.de)
                temp = self.de.n
                self.de.n = self.de.nnn
                self.do_attack(self.de, self.at)
                self.de.n = temp
                if self.at.n <= 0:
                    if self.de.n <= 0:
                        return 0
                    else:
                        return -self.de.n
                if self.de.n <= 0:
                    return self.at.n
            return -self.de.n
        
    def n_battles(self, n=10000):
        at = 0
        de = 0
        a_surv = 0
        d_surv = 0
        for i in range(n):
            r = self.battle()
            if r > 0:
                at += 1
                a_surv += r
            else:
                de += 1
                d_surv -= r
            self.at.n = self.at.nn
            self.de.n = self.de.nn

        print("Attacker: %.2f%% (surv. %.2f)\tDefender: %.2f%% (surv. %.2f)"%(at/n*100, a_surv/(at+1), de/n*100, d_surv/(de+1)))

    @classmethod
    def do_battle(cls, at, de, n=10000):
        b = cls(at, de)
        b.n_battles(n=n)
        

