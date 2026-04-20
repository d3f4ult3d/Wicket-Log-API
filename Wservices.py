
from __future__ import annotations
from typing import Any, Dict, List
from Wdata import BALL_EVENTS, INNINGS_BY_ID
from Wmodels import WicketEvent, WicketLogResponse
from cricket_utils import is_wicket, safe_int, safe_str

NO_BOWLER_CREDIT = {"run_out", "retired_hurt", "obstructing_field"}
NO_FIELDER_TYPES = {"bowled", "lbw", "hit_wicket"}


class InningsNotFoundError(Exception):
    pass


class WicketService:

    def get_wicket_log(self, innings_id: int) -> WicketLogResponse:
        innings = INNINGS_BY_ID.get(innings_id)
        if not innings:
            raise InningsNotFoundError(innings_id)
        balls   = BALL_EVENTS.get(innings_id, [])
        wickets = self._build_wicket_log(balls)
        return WicketLogResponse(
            innings_id     = innings_id,
            innings_number = safe_int(innings.get("innings_number")),
            batting_team   = safe_str(innings.get("batting_team"), "TBD"),
            bowling_team   = safe_str(innings.get("bowling_team"), "TBD"),
            total_wickets  = len(wickets),
            wickets        = wickets,
        )

    @staticmethod
    def _build_wicket_log(rows: List[Dict[str, Any]]) -> List[WicketEvent]:
        wickets      = []
        running_runs = 0
        wicket_count = 0
        rows_have_wicket_flags = any("is_wicket" in row for row in rows)
        for row in rows:
            running_runs += safe_int(row.get("runs_scored")) + safe_int(row.get("extras"))
            if rows_have_wicket_flags and not is_wicket(row):
                continue
            wicket_count += 1
            wicket_type   = safe_str(row.get("wicket_type"), "unknown").lower()
            bowler  = safe_str(row.get("bowler_name"))  if wicket_type not in NO_BOWLER_CREDIT else ""
            fielder = safe_str(row.get("fielder_name")) if wicket_type not in NO_FIELDER_TYPES  else ""
            wickets.append(WicketEvent(
                wicket_number    = wicket_count,
                over_ball        = WicketService._format_over_ball(
                    safe_int(row.get("over_number")),
                    safe_int(row.get("ball_number")),
                ),
                score_at_fall    = f"{running_runs}/{wicket_count}",
                dismissed_player = safe_str(row.get("batsman_name"), "Unknown"),
                wicket_type      = wicket_type,
                bowler           = bowler or None,
                fielder          = fielder or None,
                notes            = safe_str(row.get("notes")) or None,
            ))
        return wickets

    @staticmethod
    def _format_over_ball(over_number: int, ball_number: int) -> str:
        over_number = safe_int(over_number)
        ball_number = safe_int(ball_number)
        return f"{over_number}.{ball_number}"
