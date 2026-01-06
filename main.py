from grid import Grid
from agents import Dek, Predator, Thia, Adversary, Monster
from simulation import Simulation
from visualizer import Visualizer
import random


def main():
    random.seed(42)
    grid = Grid(25, 25)
    thia = Thia(grid, position=(2, 2), is_damaged=True)
    dek = Dek(grid, position=(1, 1), thia=thia)
    father = Predator(grid, position=(3, 3), name="Father", role="elder")
    brother = Predator(grid, position=(4, 4), name="Brother", role="peer")
    adversary = Adversary(grid, position=(20, 20))

    monsters = []
    monster_positions = [(10, 10), (15, 5), (5, 15), (12, 18), (8, 8)]
    for i, pos in enumerate(monster_positions):
        monsters.append(Monster(grid, position=pos, name=f"Monster_{i + 1}"))

    sim = Simulation(grid=grid, dek=dek, thia=thia, predators=[father, brother], adversary=adversary, monsters=monsters)
    viz = Visualizer(sim)

    print("=" * 60)
    print("PREDATOR: BADLANDS SIMULATION")
    print("=" * 60)
    print(f"\nDek's Quest: Defeat the Ultimate Adversary and restore honor")
    print(f"Grid Size: {grid.width}x{grid.height}")
    print(f"Agents: Dek, Thia, {len(sim.predators)} Predators, {len(monsters)} Monsters, 1 Adversary")
    print("=" * 60)

    max_turns = 200
    for turn in range(1, max_turns + 1):
        print(f"\n--- Turn {turn} ---")
        continue_sim = sim.step()

        if turn % 10 == 0 or not continue_sim:
            viz.display_stats()
            viz.display_grid()

        if not continue_sim:
            print("\n" + "=" * 60)
            print("SIMULATION COMPLETE")
            print("=" * 60)
            sim.print_final_report()
            break
    else:
        print("\n" + "=" * 60)
        print("SIMULATION ENDED - Maximum turns reached")
        print("=" * 60)
        sim.print_final_report()

    viz.display_grid()
    viz.plot_statistics()


if __name__ == "__main__":
    main()