import tkinter as tk
from tkinter import messagebox
from team_balancer import all_players, generate_balanced_teams, display_teams, filter_and_validate_positions

TEAM_SIZE = 6

class TeamBalancerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Team Picker")

        self.selected_ids = []
        self.vars = {}

        label = tk.Label(root, text="Select players for the match:")
        label.pack()

        self.scroll_frame = tk.Frame(root)
        self.scroll_frame.pack()

        canvas = tk.Canvas(self.scroll_frame, width=300, height=400)
        scrollbar = tk.Scrollbar(self.scroll_frame, command=canvas.yview)
        self.list_frame = tk.Frame(canvas)

        self.list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for player in all_players:
            var = tk.IntVar()
            cb = tk.Checkbutton(self.list_frame, text=f"{player['Name']} ({', '.join(player['Position'])})", variable=var)
            cb.pack(anchor="w")
            self.vars[player['Id']] = var

        gen_button = tk.Button(root, text="Generate Teams", command=self.generate_teams)
        gen_button.pack(pady=10)

        self.output = tk.Text(root, height=20, width=60)
        self.output.pack()

    def generate_teams(self):
        selected = [pid for pid, var in self.vars.items() if var.get()]
        if len(selected) != TEAM_SIZE * 2:
            messagebox.showerror("Selection Error", f"Select exactly {TEAM_SIZE * 2} players.")
            return

        from team_balancer import all_players, POSITIONS_ALLOWED, filter_and_validate_positions
        players_today = [filter_and_validate_positions(p, POSITIONS_ALLOWED) for p in all_players if p["Id"] in selected]
        combos = generate_balanced_teams(players_today)

        self.output.delete("1.0", tk.END)
        for idx, (team1, team2, t1_avg, t2_avg, diff) in enumerate(combos, 1):
            self.output.insert(tk.END, f"\n--- Option {idx} (Diff: {diff:.2f}) ---\n")
            self.output.insert(tk.END, f"\nTeam 1 (avg: {t1_avg:.2f}):\n")
            for p in team1:
                self.output.insert(tk.END, f"  - {p['Name']} ({', '.join(p['Position'])})\n")
            self.output.insert(tk.END, f"\nTeam 2 (avg: {t2_avg:.2f}):\n")
            for p in team2:
                self.output.insert(tk.END, f"  - {p['Name']} ({', '.join(p['Position'])})\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = TeamBalancerUI(root)
    root.mainloop()