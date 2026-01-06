class YautjaClanCode:

    @staticmethod
    def check_hunt_worthy(target):
        return target.health > 20 and hasattr(target, 'max_health') and target.health > target.max_health * 0.3

    @staticmethod
    def check_fighting_chance(hunter, target):
        return target.is_alive and target.health > 15

    @staticmethod
    def check_territory_respect(agent, other_trophies):
        return True

    @staticmethod
    def check_harm_unworthy(target):
        if hasattr(target, 'health') and target.health < 15:
            return False
        return True

    @staticmethod
    def evaluate_violation(agent, action, target=None):
        violations = []

        if action == "hunt" and target:
            if not YautjaClanCode.check_hunt_worthy(target):
                violations.append("Hunted unworthy prey")
            if not YautjaClanCode.check_harm_unworthy(target):
                violations.append("Harmed the unworthy")

        return violations


class Simulation:

    def __init__(self, grid, dek, thia, predators, adversary, monsters):
        self.grid = grid
        self.dek = dek
        self.thia = thia
        self.predators = predators
        self.adversary = adversary
        self.monsters = monsters

        self.turn = 0
        self.clan_honor = 50
        self.clan_code = YautjaClanCode()
        self.victory = False
        self.defeat = False

        self.stats = {
            "dek_kills": 0,
            "predator_kills": 0,
            "dek_damage_taken": 0,
            "dek_damage_dealt": 0,
            "honor_changes": [],
            "reputation_changes": []
        }

    def step(self):
        self.turn += 1

        if not self.dek.is_alive:
            print("\n*** DEK HAS FALLEN. Quest failed. ***")
            self.defeat = True
            return False

        if not self.adversary.is_alive:
            print("\n*** ADVERSARY DEFEATED! Dek's honor restored! ***")
            self.victory = True
            return False

        if self.dek.is_alive:
            action = self.dek.decide_action(self)
            old_health = self.dek.health
            self.dek.execute_action(action, self)

            if self.dek.health < old_health:
                self.stats["dek_damage_taken"] += (old_health - self.dek.health)

            if action.get("type") == "hunt":
                violations = self.clan_code.evaluate_violation(self.dek, "hunt", action.get("target"))
                if violations:
                    self.dek.reputation -= 10
                    self.clan_honor -= 5
                    print(f"Clan Code Violation: {', '.join(violations)}")
                    print(f"Dek's reputation decreased to {self.dek.reputation}")

        if self.thia and self.thia.is_alive:
            thia_action = self.thia.decide_action(self)
            self.thia.execute_action(thia_action, self)

        for predator in self.predators:
            if predator.is_alive:
                predator_action = predator.decide_action(self)
                predator.execute_action(predator_action, self)

        for monster in self.monsters:
            if monster.is_alive:
                monster_action = monster.decide_action(self)
                monster.execute_action(monster_action, self)

        if self.adversary.is_alive:
            adversary_action = self.adversary.decide_action(self)
            self.adversary.execute_action(adversary_action, self)

        return True

    def get_all_agents(self):
        agents = [self.dek]

        if self.thia:
            agents.append(self.thia)

        agents.extend(self.predators)
        agents.extend(self.monsters)
        agents.append(self.adversary)

        return agents

    def print_final_report(self):
        print("\n" + "=" * 60)
        print("FINAL REPORT")
        print("=" * 60)
        print(f"Total Turns: {self.turn}")
        print(f"Dek Status: {'ALIVE' if self.dek.is_alive else 'DEFEATED'}")
        print(f"Dek Health: {self.dek.health}/{self.dek.max_health}")
        print(f"Dek Reputation: {self.dek.reputation}")
        print(f"Dek Trophies: {len(self.dek.trophies)} - {self.dek.trophies}")
        print(f"Clan Honor: {self.clan_honor}")
        print(f"Adversary Status: {'DEFEATED' if not self.adversary.is_alive else 'ALIVE'}")

        if self.victory:
            print("\n*** VICTORY: Dek has restored his honor! ***")
        elif self.defeat:
            print("\n*** DEFEAT: Dek has fallen in battle. ***")
        else:
            print("\n*** SIMULATION INCOMPLETE ***")

        print("=" * 60)