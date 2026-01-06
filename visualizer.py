import matplotlib.pyplot as plt


class Visualizer:

    def __init__(self, simulation):
        self.sim = simulation
        self.history = {
            "turns": [],
            "dek_health": [],
            "dek_stamina": [],
            "dek_reputation": [],
            "clan_honor": [],
            "adversary_health": [],
            "monsters_alive": []
        }

    def display_grid(self):
        print("\n" + "=" * 60)
        print("GRID STATE")
        print("=" * 60)

        grid = self.sim.grid

        display = []
        for y in range(grid.height):
            row = []
            for x in range(grid.width):
                cell = grid.cells[x][y]
                if cell.occupant:
                    row.append(str(cell.occupant))
                else:
                    row.append(cell.terrain.value)
            display.append(row)

        print("   ", end="")
        for x in range(min(grid.width, 25)):
            print(f"{x % 10}", end=" ")
        print()

        for y, row in enumerate(display[:25]):
            print(f"{y:2} ", end="")
            for cell in row[:25]:
                print(cell, end=" ")
            print()

        print("\nLegend:")
        print("  D = Dek   T = Thia   F = Father   B = Brother")
        print("  M = Monster   A = Adversary")
        print("  . = Empty   ~ = Desert   ^ = Rocky   X = Trap   # = Hostile")
        print("=" * 60)

    def display_stats(self):
        print("\n" + "-" * 60)
        print("STATISTICS")
        print("-" * 60)
        print(f"Turn: {self.sim.turn}")
        print(f"Clan Honor: {self.sim.clan_honor}")
        print()
        print(f"Dek - Health: {self.sim.dek.health}/{self.sim.dek.max_health} | "
              f"Stamina: {self.sim.dek.stamina}/{self.sim.dek.max_stamina} | "
              f"Reputation: {self.sim.dek.reputation}")
        print(f"      Trophies: {len(self.sim.dek.trophies)} | "
              f"Carrying Thia: {self.sim.dek.is_carrying_thia}")
        print()

        if self.sim.thia:
            print(f"Thia - Health: {self.sim.thia.health}/{self.sim.thia.max_health} | "
                  f"Status: {'Operational' if self.sim.thia.is_alive else 'Destroyed'}")

        print(f"\nAdversary - Health: {self.sim.adversary.health}/{self.sim.adversary.max_health}")

        monsters_alive = sum(1 for m in self.sim.monsters if m.is_alive)
        print(f"Monsters - Alive: {monsters_alive}/{len(self.sim.monsters)}")

        predators_alive = sum(1 for p in self.sim.predators if p.is_alive)
        print(f"Predators - Active: {predators_alive}/{len(self.sim.predators)}")

        print("-" * 60)

        self.history["turns"].append(self.sim.turn)
        self.history["dek_health"].append(self.sim.dek.health)
        self.history["dek_stamina"].append(self.sim.dek.stamina)
        self.history["dek_reputation"].append(self.sim.dek.reputation)
        self.history["clan_honor"].append(self.sim.clan_honor)
        self.history["adversary_health"].append(self.sim.adversary.health)
        self.history["monsters_alive"].append(monsters_alive)

    def plot_statistics(self):
        if len(self.history["turns"]) < 2:
            print("Insufficient data for plotting.")
            return

        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Predator: Badlands Simulation Statistics', fontsize=16)

        turns = self.history["turns"]

        axes[0, 0].plot(turns, self.history["dek_health"], 'b-', linewidth=2)
        axes[0, 0].set_title("Dek's Health")
        axes[0, 0].set_xlabel("Turn")
        axes[0, 0].set_ylabel("Health")
        axes[0, 0].grid(True)
        axes[0, 0].set_ylim(0, self.sim.dek.max_health)

        axes[0, 1].plot(turns, self.history["dek_stamina"], 'g-', linewidth=2)
        axes[0, 1].set_title("Dek's Stamina")
        axes[0, 1].set_xlabel("Turn")
        axes[0, 1].set_ylabel("Stamina")
        axes[0, 1].grid(True)
        axes[0, 1].set_ylim(0, self.sim.dek.max_stamina)

        axes[0, 2].plot(turns, self.history["dek_reputation"], 'orange', linewidth=2)
        axes[0, 2].set_title("Dek's Reputation")
        axes[0, 2].set_xlabel("Turn")
        axes[0, 2].set_ylabel("Reputation")
        axes[0, 2].grid(True)
        axes[0, 2].axhline(y=70, color='r', linestyle='--', label='Honor Threshold')
        axes[0, 2].legend()

        axes[1, 0].plot(turns, self.history["clan_honor"], 'purple', linewidth=2)
        axes[1, 0].set_title("Clan Honor")
        axes[1, 0].set_xlabel("Turn")
        axes[1, 0].set_ylabel("Honor")
        axes[1, 0].grid(True)
        axes[1, 0].set_ylim(0, 100)

        axes[1, 1].plot(turns, self.history["adversary_health"], 'r-', linewidth=2)
        axes[1, 1].set_title("Adversary Health")
        axes[1, 1].set_xlabel("Turn")
        axes[1, 1].set_ylabel("Health")
        axes[1, 1].grid(True)
        axes[1, 1].set_ylim(0, self.sim.adversary.max_health)

        axes[1, 2].plot(turns, self.history["monsters_alive"], 'brown', linewidth=2)
        axes[1, 2].set_title("Monsters Alive")
        axes[1, 2].set_xlabel("Turn")
        axes[1, 2].set_ylabel("Count")
        axes[1, 2].grid(True)
        axes[1, 2].set_ylim(0, len(self.sim.monsters) + 1)

        plt.tight_layout()
        plt.savefig('simulation_statistics.png', dpi=300, bbox_inches='tight')
        print("\nStatistics plot saved as 'simulation_statistics.png'")
        plt.show()