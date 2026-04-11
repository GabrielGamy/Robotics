# Toy Robot Workspace (ROS 2)

Ce workspace contient le package `toy_robot`.

## Workflow rapide apres chaque changement

1. Sauvegarder le fichier.
2. Dans `toy_robot_ws`, rebuild le package.
3. Recharger l'environnement.
4. Relancer le noeud concerne.

Commandes:

cd <root>/src/robotics/toy_robot_ws
colcon build --packages-select toy_robot --symlink-install
source install/setup.bash
ros2 run toy_robot brain_node

Exemples de relance de noeud:

ros2 run toy_robot perception_node
ros2 run toy_robot fake_navigation_server

## Notes utiles

- Ouvrir un nouveau terminal => relancer `source install/setup.bash`.
- Si tu modifies `setup.py`, `package.xml`, ou ajoutes un nouveau noeud: rebuild + source obligatoires.
