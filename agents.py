import random
from abc import ABC, abstractmethod


class Agent(ABC):

    def __init__(self, grid, position, name="Agent"):
        self.grid = grid
        self.position = position
        self.name = name
        self.health = 100
        self.max_health = 100
        self.is_alive = True
        grid.place_agent(self, position)

    @abstractmethod
    def decide_action(self, simulation):
        pass

    @abstractmethod
    def execute_action(self, action, simulation):
        pass

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.is_alive = False
            self.grid.remove_agent(self.position)

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def __repr__(self):
        return self.name[0]


class Predator(Agent):

    def __init__(self, grid, position, name="Predator", role="peer"):
        super().__init__(grid, position, name)
        self.role = role
        self.stamina = 100
        self.max_stamina = 100
        self.reputation = 80
        self.trophies = []
        self.clan_code_violations = 0
        self.target = None

    def decide_action(self, simulation):
        dek = simulation.dek

        if self._check_dek_violations(dek, simulation):
            return {"type": "challenge", "target": dek}

        monsters = [m for m in simulation.monsters if m.is_alive]
        if monsters and random.random() < 0.4:
            closest = min(monsters, key=lambda m: self.grid.get_distance(self.position, m.position))
            if self.grid.get_distance(self.position, closest.position) <= 2:
                return {"type": "hunt", "target": closest}
            else:
                return {"type": "move_towards", "target": closest.position}

        return {"type": "patrol"}

    def execute_action(self, action, simulation):
        action_type = action["type"]

        if action_type == "patrol":
            self._patrol()
        elif action_type == "move_towards":
            self._move_towards(action["target"])
        elif action_type == "hunt":
            self._hunt_target(action["target"], simulation)
        elif action_type == "challenge":
            self._challenge_dek(action["target"], simulation)

    def _patrol(self):
        if self.stamina < 5:
            return

        neighbors = self.grid.get_neighbors(*self.position)
        passable = [(x, y, c) for x, y, c in neighbors if c.is_passable()]

        if passable:
            x, y, cell = random.choice(passable)
            cost = self.grid.move_agent(self.position, (x, y))
            self.stamina -= cost

    def _move_towards(self, target_pos):
        if self.stamina < 5:
            return

        x, y = self.position
        tx, ty = target_pos

        dx = 1 if tx > x else -1 if tx < x else 0
        dy = 1 if ty > y else -1 if ty < y else 0

        new_pos = (x + dx, y + dy)
        cell = self.grid.get_cell(*new_pos)

        if cell.is_passable():
            cost = self.grid.move_agent(self.position, new_pos)
            self.stamina -= cost

    def _hunt_target(self, target, simulation):
        if not target.is_alive:
            return

        hit_chance = 0.7
        damage = random.randint(20, 40)

        if random.random() < hit_chance:
            target.take_damage(damage)
            print(f"{self.name} attacks {target.name} for {damage} damage!")

            if not target.is_alive:
                print(f"{self.name} defeated {target.name}!")
                self.trophies.append(target.name)
                self.reputation += 5
                simulation.clan_honor += 10

        self.stamina -= 10

    def _challenge_dek(self, dek, simulation):
        print(f"\n{self.name} challenges Dek!")

        if self.clan_code_violations > 0:
            dek.reputation -= 15
            print(f"Dek's reputation reduced for code violation.")
        else:
            if dek.reputation > self.reputation:
                dek.reputation += 5
                print(f"Dek proves worthy. Reputation increased.")
            else:
                dek.reputation -= 10
                print(f"Dek fails the challenge. Reputation decreased.")

    def _check_dek_violations(self, dek, simulation):
        if dek.reputation < 30:
            return random.random() < 0.3
        return False


class Dek(Agent):

    def __init__(self, grid, position, thia=None):
        super().__init__(grid, position, "Dek")
        self.stamina = 100
        self.max_stamina = 100
        self.reputation = 50
        self.trophies = []
        self.is_carrying_thia = False
        self.thia = thia
        self.code_violations = []

    def decide_action(self, simulation):
        if self.health < 40 and self.stamina > 20:
            return {"type": "rest"}

        if self.thia and self.thia.is_alive and not self.is_carrying_thia:
            dist = self.grid.get_distance(self.position, self.thia.position)
            if dist <= 1:
                return {"type": "carry_thia"}
            elif dist <= 5:
                return {"type": "move_towards", "target": self.thia.position}

        adversary = simulation.adversary
        if adversary.is_alive:
            dist = self.grid.get_distance(self.position, adversary.position)
            if dist <= 2:
                return {"type": "fight", "target": adversary}
            elif self.health > 60 and self.stamina > 40:
                return {"type": "move_towards", "target": adversary.position}

        monsters = [m for m in simulation.monsters if m.is_alive]
        if monsters and self.stamina > 30:
            worthy = [m for m in monsters if m.health > 30]
            if worthy:
                closest = min(worthy, key=lambda m: self.grid.get_distance(self.position, m.position))
                dist = self.grid.get_distance(self.position, closest.position)
                if dist <= 2:
                    return {"type": "hunt", "target": closest}
                else:
                    return {"type": "move_towards", "target": closest.position}

        if adversary.is_alive:
            return {"type": "move_towards", "target": adversary.position}

        return {"type": "rest"}

    def execute_action(self, action, simulation):
        action_type = action["type"]

        if action_type == "rest":
            self._rest()
        elif action_type == "move_towards":
            self._move_towards(action["target"], simulation)
        elif action_type == "carry_thia":
            self._carry_thia()
        elif action_type == "hunt":
            self._hunt_target(action["target"], simulation)
        elif action_type == "fight":
            self._fight_adversary(action["target"], simulation)

    def _rest(self):
        self.stamina = min(self.max_stamina, self.stamina + 15)
        self.health = min(self.max_health, self.health + 5)

    def _move_towards(self, target_pos, simulation):
        if self.stamina < 3:
            return

        x, y = self.position
        tx, ty = target_pos

        dx = 1 if tx > x else -1 if tx < x else 0
        dy = 1 if ty > y else -1 if ty < y else 0

        new_pos = (x + dx, y + dy)
        cell = self.grid.get_cell(*new_pos)

        if cell.is_passable():
            cost = self.grid.move_agent(self.position, new_pos)

            if self.is_carrying_thia:
                cost += 2

            self.stamina -= cost

            if cell.is_trap:
                trap_damage = random.randint(10, 20)
                self.take_damage(trap_damage)
                print(f"Dek triggered a trap! Lost {trap_damage} health.")

            if self.is_carrying_thia and self.thia:
                self.thia.position = new_pos

    def _carry_thia(self):
        if self.thia and not self.is_carrying_thia:
            dist = self.grid.get_distance(self.position, self.thia.position)
            if dist <= 1:
                self.is_carrying_thia = True
                print(f"Dek is now carrying Thia.")

    def _hunt_target(self, target, simulation):
        if not target.is_alive:
            return

        if target.health < 20:
            print(f"Dek refuses to hunt weakened {target.name} (Clan Code: Hunt the Worthy)")
            self.code_violations.append("Attempted unworthy hunt")
            return

        hit_chance = 0.75
        damage = random.randint(25, 45)

        if random.random() < hit_chance:
            target.take_damage(damage)
            print(f"Dek hunts {target.name} for {damage} damage!")

            if not target.is_alive:
                print(f"Dek defeated {target.name}! Trophy claimed.")
                self.trophies.append(target.name)
                self.reputation += 10
                simulation.clan_honor += 5
        else:
            print(f"Dek's attack missed!")

        self.stamina -= 12

        if target.is_alive and random.random() < 0.4:
            counter_damage = random.randint(10, 25)
            self.take_damage(counter_damage)
            print(f"{target.name} counter-attacks for {counter_damage} damage!")

    def _fight_adversary(self, adversary, simulation):
        if not adversary.is_alive:
            return

        print(f"\nDek engages the Ultimate Adversary!")

        hit_chance = 0.6
        if self.thia and self.thia.is_alive and self.is_carrying_thia:
            hit_chance = 0.75
            print("Thia provides tactical support!")

        damage = random.randint(30, 50)

        if random.random() < hit_chance:
            adversary.take_damage(damage)
            print(f"Dek strikes the adversary for {damage} damage!")

            if not adversary.is_alive:
                print(f"\n*** DEK DEFEATS THE ULTIMATE ADVERSARY! ***")
                self.reputation += 50
                simulation.clan_honor += 100
                simulation.victory = True
        else:
            print(f"Dek's attack missed the adversary!")

        self.stamina -= 15


class Thia(Agent):

    def __init__(self, grid, position, is_damaged=True):
        super().__init__(grid, position, "Thia")
        self.is_damaged = is_damaged
        self.can_move = not is_damaged
        self.knowledge_database = self._initialize_knowledge()
        self.reconnaissance_data = {}

    def _initialize_knowledge(self):
        return {
            "adversary_weakness": "Sustained attacks to central mass",
            "trap_locations": [],
            "terrain_hazards": "Rocky zones drain stamina significantly",
            "clan_code_summary": "Honor through worthy combat"
        }

    def decide_action(self, simulation):
        if random.random() < 0.2:
            return {"type": "reconnaissance"}
        return {"type": "idle"}

    def execute_action(self, action, simulation):
        if action["type"] == "reconnaissance":
            self._perform_reconnaissance(simulation)

    def _perform_reconnaissance(self, simulation):
        x, y = self.position

        for dx in range(-3, 4):
            for dy in range(-3, 4):
                cell = self.grid.get_cell(x + dx, y + dy)
                if cell.is_trap:
                    if (x + dx, y + dy) not in self.knowledge_database["trap_locations"]:
                        self.knowledge_database["trap_locations"].append((x + dx, y + dy))
                        print("Thia detected a trap nearby.")

    def provide_support(self, dek):
        if not self.is_alive:
            return

        if random.random() < 0.3:
            advice = random.choice(list(self.knowledge_database.values()))
            print(f"Thia advises: {advice}")

    def __repr__(self):
        return "T"


class Monster(Agent):

    def __init__(self, grid, position, name="Monster"):
        super().__init__(grid, position, name)
        self.aggression = random.uniform(0.3, 0.8)
        self.health = random.randint(40, 80)
        self.max_health = self.health

    def decide_action(self, simulation):
        nearest_agent = None
        min_dist = float('inf')

        for agent in simulation.get_all_agents():
            if agent != self and agent.is_alive:
                dist = self.grid.get_distance(self.position, agent.position)
                if dist < min_dist:
                    min_dist = dist
                    nearest_agent = agent

        if nearest_agent and min_dist <= 2 and random.random() < self.aggression:
            return {"type": "attack", "target": nearest_agent}

        return {"type": "wander"}

    def execute_action(self, action, simulation):
        if action["type"] == "wander":
            self._wander()
        elif action["type"] == "attack":
            self._attack(action["target"])

    def _wander(self):
        neighbors = self.grid.get_neighbors(*self.position)
        passable = [(x, y, c) for x, y, c in neighbors if c.is_passable()]

        if passable:
            x, y, _ = random.choice(passable)
            self.grid.move_agent(self.position, (x, y))

    def _attack(self, target):
        damage = random.randint(15, 30)
        target.take_damage(damage)
        print(f"{self.name} attacks {target.name} for {damage} damage!")

    def __repr__(self):
        return "M"


class Adversary(Agent):

    def __init__(self, grid, position):
        super().__init__(grid, position, "Adversary")
        self.health = 300
        self.max_health = 300
        self.resilience = 0.3
        self.territory_center = position
        self.territory_radius = 5
        self.attack_pattern = 0

    def decide_action(self, simulation):
        dek = simulation.dek

        dist_to_dek = self.grid.get_distance(self.position, dek.position)

        if dist_to_dek <= 3:
            return {"type": "attack", "target": dek}
        elif dist_to_dek <= self.territory_radius:
            return {"type": "move_towards", "target": dek.position}
        else:
            return {"type": "patrol_territory"}

    def execute_action(self, action, simulation):
        action_type = action["type"]

        if action_type == "patrol_territory":
            self._patrol_territory()
        elif action_type == "move_towards":
            self._move_towards(action["target"])
        elif action_type == "attack":
            self._attack(action["target"])

    def _patrol_territory(self):
        x, y = self.position
        tx, ty = self.territory_center

        if self.grid.get_distance((x, y), (tx, ty)) > self.territory_radius:
            self._move_towards((tx, ty))
        else:
            neighbors = self.grid.get_neighbors(*self.position)
            passable = [(nx, ny, c) for nx, ny, c in neighbors if c.is_passable()]
            if passable:
                nx, ny, _ = random.choice(passable)
                self.grid.move_agent(self.position, (nx, ny))

    def _move_towards(self, target_pos):
        x, y = self.position
        tx, ty = target_pos

        dx = 1 if tx > x else -1 if tx < x else 0
        dy = 1 if ty > y else -1 if ty < y else 0

        new_pos = (x + dx, y + dy)
        cell = self.grid.get_cell(*new_pos)

        if cell.is_passable():
            self.grid.move_agent(self.position, new_pos)

    def _attack(self, target):
        self.attack_pattern = (self.attack_pattern + 1) % 3

        if self.attack_pattern == 0:
            damage = random.randint(35, 50)
            print(f"Adversary unleashes devastating strike!")
        elif self.attack_pattern == 1:
            damage = random.randint(25, 40)
            print(f"Adversary performs area sweep!")
        else:
            damage = random.randint(30, 45)
            print(f"Adversary lunges with crushing force!")

        target.take_damage(damage)
        print(f"Adversary deals {damage} damage to {target.name}!")

    def take_damage(self, amount):
        reduced_damage = int(amount * (1 - self.resilience))
        super().take_damage(reduced_damage)
        print(f"Adversary's resilience reduces damage to {reduced_damage}!")

    def __repr__(self):
        return "A"