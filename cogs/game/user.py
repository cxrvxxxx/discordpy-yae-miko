from __future__ import annotations

from typing import Tuple
from math import floor
from random import randint

class User(object):
    def __init__(self, uid, level, exp, cash, bank):
        self.__uid = uid
        self.__level = level
        self.__exp = exp
        self.__cash = cash
        self.__bank = bank

    @property
    def uid(self) -> int:
        return self.__uid
    
    @property
    def level(self) -> int:
        return self.__level
    
    @property
    def exp(self) -> int:
        return self.__exp
    
    @property
    def cash(self) -> int:
        return self.__cash
    
    @property
    def bank(self) -> int:
        return self.__bank
    
    @property
    def exp_cap(self) -> int:
        return 2 * pow(self.level, 2) + 2 * self.level + 2
    
    @level.setter
    def level(self, value: int) -> None:
        if value < 0:
            return
        
        self.__level = value

    @exp.setter
    def exp(self, value: int) -> None:
        if value < 0:
            return
        
        self.__exp = value

    @cash.setter
    def cash(self, value: int) -> None:
        if value < 0:
            return
        
        self.__cash = value

    @bank.setter
    def bank(self, value: int) -> None:
        if value < 0:
            return
        
        self.__bank = value

    def add_exp(self, value) -> bool:
        if value < 0:
            return
        
        flag = False
        self.exp += value
        while self.exp >= self.exp_cap:
            self.exp -= self.exp_cap
            self.level += 1
            flag = True

        return flag


    def work(self, multiplier: float = 1.0) -> Tuple[int, int, bool]:
        multiplier = 1.0 if multiplier < 0 else multiplier
        exp = floor(randint(self.level, self.level * 1.5) * multiplier)
        cash = floor(randint(self.level, self.level * 3)* multiplier)

        levelup = self.add_exp(exp)
        self.cash += cash

        return exp, cash, levelup

    def deposit(self, value: int) -> bool:
        if self.cash < value:
            return False
        
        self.cash -= value
        self.bank += value
        
        return True
    
    def withdraw(self, value: int) -> bool:
        if self.bank < value:
            return False
        
        self.bank -= value
        self.cash += value

        return True
    
    def transfer(self, target: User, value: int) -> bool:
        if self.cash < value:
            return False
        
        self.cash -= value
        target.cash += value

        return True
    
    def rob(self, target: User):
        amount = floor(randint(self.level, self.level * 1.5))
        is_failed = True if randint(1, 100) > 50 else False

        self.cash += amount if not is_failed else amount * -1
        target.cash -= self.cash - amount if not is_failed else amount * -1

        return is_failed, amount
    
    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, User):
            if (
                self.uid == obj.uid and
                self.level == obj.level and
                self.exp == obj.exp and
                self.cash == obj.cash and
                self.bank == obj.bank
            ): return True

        return False
    
    def __str__(self) -> str:
        return f'{self.uid}, {self.level}, {self.exp}, {self.cash}, {self.bank}'
