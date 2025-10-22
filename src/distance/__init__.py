"""Distance module - Distance calculations."""

from typing import Optional


class DistanceCalculator:
    """Calculate distances between systems using 3D coordinates."""

    @staticmethod
    def calculate_distance(
        x1: Optional[float],
        y1: Optional[float],
        z1: Optional[float],
        x2: Optional[float],
        y2: Optional[float],
        z2: Optional[float],
    ) -> Optional[float]:
        """
        Calculate distance between two 3D points in light years.

        Args:
            x1, y1, z1: Coordinates of first system.
            x2, y2, z2: Coordinates of second system.

        Returns:
            Distance in light years, or None if coordinates are incomplete.
        """
        if any(coord is None for coord in [x1, y1, z1, x2, y2, z2]):
            return None

        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1

        distance = (dx**2 + dy**2 + dz**2) ** 0.5
        return round(distance, 2)

    @staticmethod
    def format_distance(distance: Optional[float]) -> str:
        """
        Format distance for display.

        Args:
            distance: Distance in light years.

        Returns:
            Formatted string representation.
        """
        if distance is None:
            return "Unknown"
        return f"{distance:.2f} ly"
