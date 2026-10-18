from setuptools import find_packages, setup

package_name = 'toy_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/robot.launch.xml']),
        ('share/' + package_name + '/config', ['config/robot_config.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='gabrielgamy',
    maintainer_email='gabrielgamy@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'brain_node = toy_robot.nodes.brain_node:main',
            'manipulation_node = toy_robot.nodes.manipulation_node:main',
            'perception_node = toy_robot.nodes.perception_node:main',
        ],
    },
)
