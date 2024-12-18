import pygame
import numpy as np


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other_point):
        return np.sqrt((self.x - other_point.x) ** 2 + (self.y - other_point.y) ** 2)


def dbscan_custom(points, eps, min_samples):
    def region_query(point, points, eps):
        neighbors = []
        for other_point in points:
            if point.distance(other_point) <= eps:
                neighbors.append(other_point)
        return neighbors

    def expand_cluster(point, neighbors, cluster_id, clusters, visited, eps, min_samples):
        clusters[point] = cluster_id
        i = 0
        while i < len(neighbors):
            neighbor = neighbors[i]
            if neighbor not in visited:
                visited.add(neighbor)
                new_neighbors = region_query(neighbor, points, eps)
                if len(new_neighbors) >= min_samples:
                    neighbors.extend(new_neighbors)
            if neighbor not in clusters:
                clusters[neighbor] = cluster_id
            i += 1

    clusters = {}
    visited = set()
    cluster_id = 0

    for point in points:
        if point not in visited:
            visited.add(point)
            neighbors = region_query(point, points, eps)
            if len(neighbors) >= min_samples:
                cluster_id += 1
                expand_cluster(point, neighbors, cluster_id, clusters, visited, eps, min_samples)
            else:
                clusters[point] = -1  # "Шумная" точка.

    # Разделяем точки на принадлежащие кластерам, граничные и шум.
    core_points = set()
    borders = set()
    for point in points:
        if clusters[point] != -1:  # Не шум.
            neighbors = region_query(point, points, eps)
            if len(neighbors) >= min_samples:
                core_points.add(point)
            else:
                borders.add(point)

    # Генерируем метки.
    labels = []
    for point in points:
        labels.append(clusters.get(point, -1))  # -1 для шума.
    return labels, core_points, borders


def get_array(points):
    values = np.zeros((len(points), 2))
    for i in range(len(points)):
        values[i][0] = points[i].x
        values[i][1] = points[i].y
    return values


def main():
    cluster_colors = ["blue", "cyan", "purple"]
    labels_colors = ["green", "yellow", "red"]
    r = 3
    points = []
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    screen.fill("#FFFFFF")
    pygame.display.update()

    is_running = True

    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                p = Point(*pos)
                points.append(p)
                pygame.draw.circle(screen, "black", pos, r)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    labels, core_points, borders = dbscan_custom(points, eps=50, min_samples=3)
                    dbscan_result = (labels, core_points, borders)
                    for i in range(len(points)):
                        cluster_id = labels[i]
                        if cluster_id != -1:
                            color = cluster_colors[cluster_id % len(cluster_colors)]
                        else:
                            color = labels_colors[2]  # Изначально красный, т.к. шум.
                        pygame.draw.circle(screen, color, (points[i].x, points[i].y), r)

                if event.key == pygame.K_RETURN and dbscan_result:
                    labels, core_points, borders = dbscan_result
                    for i in range(len(points)):
                        point = points[i]
                        if point in core_points:
                            color = labels_colors[0]  # Зелёный для точек, принадлежащих кластерам.
                        elif point in borders:
                            color = labels_colors[1]  # Жёлтый для граничных точек.
                        else:
                            color = labels_colors[2]  # Красный для шума.
                        pygame.draw.circle(screen, color, (point.x, point.y), r)

            pygame.display.flip()


if __name__ == '__main__':
    main()
