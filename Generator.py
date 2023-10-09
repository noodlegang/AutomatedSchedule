import random

import numpy as np
import pandas as pd
import copy
import models


def initial_subject_population(all_subjects_for_week, population_size):
    subject_list_population = {}
    for i in range(population_size):
        shuffled_subjects = copy.deepcopy(all_subjects_for_week)  # Make a copy to avoid modifying the original list
        np.random.shuffle(shuffled_subjects)
        subject_list_population[i] = shuffled_subjects
    return subject_list_population


def initial_schedule_population(current_subject_offspring, rooms_list, lecturers_list):
    schedule_list_population = {}
    for i, offspring in enumerate(current_subject_offspring, 1):
        created_schedules = []  # Initialize schedules for each offspring
        id_schedule = 1
        for subject in offspring:  # Iterate through subjects in the current offspring
            room = random.choice(rooms_list)
            lecturer = random.choice(lecturers_list)
            schedule = models.Schedule(id_schedule, room.id_room, lecturer.id_lecturer, subject.id_subject)
            created_schedules.append(schedule)
            id_schedule += 1
        schedule_list_population[i] = created_schedules  # Store schedules for the current offspring
    return schedule_list_population


"""
    lets break down the problem in sections
    1. the assignment of rooms to each plan
    --plan that requires computers should be in room that has them
    2. the assignment of teacher on corresponding days
    --teacher can't teach on the day they're unavailable
"""


def subject_gets_computers(subject, room):
    if subject.needs_computers and not room.has_computers:
        return False
    return True


def lecturer_available_on_day(offspring, lecturer):
    fitness = 0
    num_parts = 5
    part_size = len(offspring) // num_parts
    my_list = copy.deepcopy(offspring)
    divided_schedule_list = [my_list[i:i + part_size] for i in range(0, len(my_list), part_size)]
    for day_num, day in enumerate(divided_schedule_list, 1):
        match day_num:
            case 1:
                if lecturer.MON: fitness += 1
            case 2:
                if lecturer.TUE: fitness += 1
            case 3:
                if lecturer.WED: fitness += 1
            case 4:
                if lecturer.THU: fitness += 1
            case 5:
                if lecturer.FRI: fitness += 1
            case _:
                print("pizdec")
    return fitness


def current_schedule_fitness(offspring, room, lecturer, subject):
    fitness = 0

    if subject_gets_computers(subject, room):
        fitness += 1
    fitness += lecturer_available_on_day(offspring, lecturer)

    return fitness


def current_offspring_fitness(schedule_list, rooms_list, lecturer_list, subject_list):
    all_fitness = []
    all_top_schedules = {}

    for i, offspring in enumerate(schedule_list):
        total_list_fitness = 0
        list_top_schedules = []
        top_fitness = 0
        top_schedule = None

        for schedule in offspring:
            room = find_room(schedule.id_room, rooms_list)
            lecturer = find_lecturer(schedule.id_lecturer, lecturer_list)
            subject = find_subject(schedule.id_subject, subject_list)

            if room is None or lecturer is None or subject is None:
                continue  # Handle missing data

            fitness = current_schedule_fitness(offspring, room, lecturer, subject)

            if fitness > top_fitness:
                top_fitness = fitness
                top_schedule = schedule

            list_top_schedules.append(top_schedule)
            total_list_fitness += 10 ** top_fitness

        all_top_schedules[i] = list_top_schedules
        all_fitness.append(total_list_fitness)

    return all_fitness, all_top_schedules


def find_room(room_id, rooms_list):
    return next((room for room in rooms_list if room.id_room == room_id), None)


def find_lecturer(lecturer_id, lecturer_list):
    return next((lecturer for lecturer in lecturer_list if lecturer.id_lecturer == lecturer_id), None)


def find_subject(subject_id, subject_list):
    return next((subject for subject in subject_list if subject.id_subject == subject_id), None)


def create_subject_list_for_week(subjects_instance):
    all_subjects_for_week = []
    for subject in subjects_instance:
        match subject.study_credits:
            case 1:
                # 3 hours = 2 lectures (1.5h for lecture)
                all_subjects_for_week.extend(subject * 2)
            case 3:
                # 9 hours
                all_subjects_for_week.extend(subject * 6)
            case 6:
                # 18hours
                all_subjects_for_week.extend(subject * 12)
            case 12:
                # 36h
                all_subjects_for_week.extend(subject * 24)
            case _:
                print("I hate python")
    return all_subjects_for_week


class Generator:
    week = {
        'Monday': [],
        'Tuesday': [],
        'Wednesday': [],
        'Thursday': [],
        'Friday': [],
    }
    df = pd.DataFrame(week)

    def __init__(self, subjects, schedules, rooms, lecturers):
        self.subjects_instance = copy.deepcopy(subjects)
        self.schedules_instance = copy.deepcopy(schedules)
        self.rooms_instance = copy.deepcopy(rooms)
        self.lecturers_instance = copy.deepcopy(lecturers)

    def generate(self):
        x_points = []
        y_points = []
        all_subjects_for_week = create_subject_list_for_week(self.subjects_instance)
        current_subject_offspring = initial_subject_population(all_subjects_for_week, 20)
        current_schedule_offspring = initial_schedule_population(current_subject_offspring, self.rooms_instance,
                                                                 self.lecturers_instance)
        counter = 20
        while counter > 0:
            fitness, top_students_dict = current_offspring_fitness(current_schedule_offspring,
                                                                   self.rooms_instance, self.lecturers_instance,
                                                                   self.subjects_instance)
