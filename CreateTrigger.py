from statemachine import StateMachine, State
from pyeda import inter as eda


class DTrigger(StateMachine):
    locked = State('Locked', initial=True)
    unlocked = State('Unlocked')
    result_Q = 0
    rule = {}

    lock = unlocked.to(locked)
    unlock = locked.to(unlocked)

    # function for adding rules from pyeda expression
    def add_rule_from_expr(self, pyeda_expr):
        self.rule = {}
        rule_tt = eda.expr2truthtable(pyeda_expr)
        for line in str(rule_tt).splitlines():
            if ':' in line:
                q = "".join(line.split(":")[-1].strip())
                x2 = "".join(line.split()[0].strip())
                x1 = "".join(line.split()[1].strip())
                self.rule[x2 + x1] = q

    # function for recording new data
    def change_last_value(self, data):
        if self.current_state == self.unlocked:
            self.result_Q = data

    # function for checking whether values match a rule
    def check_values(self, values):
        if values in self.rule:
            if self.rule[values] == '1':
                return True
        return False

    # function for change state trigger
    def change_state(self, values):
        if self.check_values(values) == True or self.rule == {}:
            if self.current_state != self.unlocked:
                self.unlock()
        else:
            if self.current_state != self.locked:
                self.lock()

    # function for working with a trigger
    def run_trigger(self, data, values):
        self.change_state(values)
        self.change_last_value(data)
        return self.result_Q

d_tr = DTrigger()
result = d_tr.run_trigger('aaaa', '0')      # write data without rules
print('result_without_rule=', result)       # search result
X = eda.exprvars('X', 2)                    # create a rule truthtable
rule_tt = eda.truthtable(X, '0100')
print('rule_table:\n', rule_tt)             # print a rule truthtable
rule_expr = eda.truthtable2expr(rule_tt)    # create a rule expression

d_tr.add_rule_from_expr(rule_expr)
result = d_tr.run_trigger('bbbb', '11')     # write data with rule and wrong values
print('result_with_rule_and_wrong_key=', result)    # data not write
result = d_tr.run_trigger('bbbb', '01')     # write data with rule and good values
print('result_with_rule_and_good_key=', result)     # data changed

