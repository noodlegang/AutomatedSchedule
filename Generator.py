import random

import numpy as np
import pandas as pd
import copy
import models


# all good
def initial_subject_population(all_subjects_for_week, population_size):
    subject_list_population = {}
    for i in range(population_size):
        shuffled_subjects = copy.deepcopy(all_subjects_for_week)  # Make a copy to avoid modifying the original list
        np.random.shuffle(shuffled_subjects)
        subject_list_population[i] = shuffled_subjects
    return subject_list_population


# all good
def initial_schedule_population(current_subject_offspring, rooms_list, lecturers_list):
    schedule_list_population = {}
    for i, offspring in enumerate(current_subject_offspring.values(), 1):
        created_schedules = []  # Initialize schedules for each offspring
        id_schedule = i
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


# not good
def lecturer_available_on_day(offspring, lecturer):
    fitness = 0
    num_parts = 5
    divided_schedule_list = slice_list_in_parts(offspring, 5, None)
    for day_num, day in enumerate(divided_schedule_list, 1):
        match day_num:
            case 1:
                if lecturer.MON: fitness += 1
                print(str(day_num) + str(lecturer.MON))
            case 2:
                if lecturer.TUE: fitness += 1
                print(str(day_num) + str(lecturer.TUE))
            case 3:
                if lecturer.WED: fitness += 1
                print(str(day_num) + str(lecturer.WED))
            case 4:
                if lecturer.THU: fitness += 1
                print(str(day_num) + str(lecturer.THU))
            case 5:
                if lecturer.FRI: fitness += 1
                print(str(day_num) + str(lecturer.FRI))
            case _:
                pass

    return fitness


# overall good me thinks
def current_schedule_fitness(offspring, room, lecturer, subject):
    fitness = 0

    if subject_gets_computers(subject, room):
        fitness += 1
    fitness += lecturer_available_on_day(offspring, lecturer)

    return fitness


def current_offspring_fitness(schedule_list, rooms_list, lecturer_list, subject_list):
    all_fitness = []
    all_top_schedules = {}

    for i, offspring in enumerate(schedule_list.values()):
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


# all good
def create_subject_list_for_week(subjects_instance):
    all_subjects_for_week = []
    for subject in subjects_instance:
        match subject.study_credits:
            case 1:
                # 3 hours = 2 lectures (1.5h for lecture)
                all_subjects_for_week.extend([subject] * 2)
            case 3:
                # 9 hours - 6
                all_subjects_for_week.extend([subject] * 6)
            case 6:
                # 18hours - 12
                all_subjects_for_week.extend([subject] * 12)
            case 12:
                # 36h - 24
                all_subjects_for_week.extend([subject] * 24)
            case _:
                print("I hate python")
    return all_subjects_for_week


# all good
def hall_of_fame(current_schedule_offspring, fitness):
    if not fitness:
        return None, -1  # Return None and -1 for empty lists

    best_index = max(range(len(fitness)), key=fitness.__getitem__)
    best_offspring = current_schedule_offspring[best_index + 1]

    return best_offspring, best_index


# all good
def crossover(offspring, offspring_fitness):
    if not offspring or not offspring_fitness:
        return {}

    total_fitness = sum(offspring_fitness)
    fitness_percentages = [fit / total_fitness for fit in offspring_fitness]

    new_offspring_dict = {}
    iterations = len(offspring)

    while iterations > 0:
        parent_indices = []
        while len(parent_indices) < 2:
            selected_index = roulette_selection(fitness_percentages)
            if selected_index != 0 and selected_index not in parent_indices:
                parent_indices.append(selected_index)
        parent_1, parent_2 = offspring[parent_indices[0]], offspring[parent_indices[1]]

        new_offspring = crossover_genes(parent_1, parent_2)
        new_offspring_dict[iterations] = new_offspring

        iterations -= 1

    return new_offspring_dict


def roulette_selection(fitness_percentages):
    random_num = random.random()
    cumulative_prob = 0.0
    for i, percentage in enumerate(fitness_percentages):
        cumulative_prob += percentage
        if random_num <= cumulative_prob:
            return i


def crossover_genes(parent_1, parent_2):
    new_offspring = []
    for gene_1, gene_2 in zip(parent_1, parent_2):
        gene = []
        if random.choice([True, False]):
            gene.append(gene_2)
        else:
            gene.append(gene_1)
        new_offspring.append(gene)
    return new_offspring


def mutate(offspring, mutation_chance, population_size):
    new_offspring_dict = {}
    for count in range(1, population_size + 1):
        new_offspring = []

        gene = offspring[count]  # Fixed indexing from population

        current_gene = gene.copy()  # Create a copy of the gene
        if random.random() < mutation_chance:
            index1, index2 = random.sample(range(6), 2)  # Generate unique indices
            current_gene[index1], current_gene[index2] = current_gene[index2], current_gene[index1]  # Swap values
        new_offspring.append(current_gene)

        new_offspring_dict[count] = new_offspring

    return new_offspring_dict


def absolute_fitness(top_doggie, rooms_list, lecturer_list, subject_list):
    total_list_fitness = 0

    for schedule in top_doggie:
        offspring_fitness = 0

        room = find_room(schedule.id_room, rooms_list)
        lecturer = find_lecturer(schedule.id_lecturer, lecturer_list)
        subject = find_subject(schedule.id_subject, subject_list)

        if room is not None and lecturer is not None and subject is not None:
            fitness = current_schedule_fitness(top_doggie, room, lecturer, subject)
            offspring_fitness = max(offspring_fitness, fitness)

        total_list_fitness += offspring_fitness

    return total_list_fitness


def slice_list_in_parts(my_list, num_of_parts, needed_part):
    sliced_list = np.array_split(my_list, num_of_parts)
    if needed_part is None:
        return sliced_list
    return sliced_list[needed_part]


def prepare_lists_for_df(top_doggie):
    sliced_list = slice_list_in_parts(top_doggie, 5, None)
    sliced_list = [item.tolist() if isinstance(item, np.ndarray) else item for item in sliced_list]
    max_length = 8
    result_lists = []

    for slice_of_the_list in sliced_list:
        while len(slice_of_the_list) != max_length:
            if len(slice_of_the_list) > max_length:
                slice_of_the_list = random.sample(slice_of_the_list, max_length)
            if len(slice_of_the_list) < max_length:
                str1 = "free time"
                slice_of_the_list.append(str1)

        result_lists.append(slice_of_the_list)

    return result_lists


class Generator:

    def __init__(self, subjects, rooms, lecturers):
        self.subjects_instance = copy.deepcopy(subjects)
        self.rooms_instance = copy.deepcopy(rooms)
        self.lecturers_instance = copy.deepcopy(lecturers)

    def generate(self):
        teacher_list = copy.deepcopy(self.lecturers_instance)
        population_size = 20
        mutation_chance = 0.4
        top_doggie = None
        top_doggie_fitness = None
        x_points = []
        y_points = []
        all_subjects_for_week = create_subject_list_for_week(self.subjects_instance)
        current_subject_offspring = initial_subject_population(all_subjects_for_week, population_size)
        current_schedule_offspring = initial_schedule_population(current_subject_offspring, self.rooms_instance,
                                                                 teacher_list)
        counter = population_size
        while counter > 0:
            fitness, top_students_dict = current_offspring_fitness(current_schedule_offspring,
                                                                   self.rooms_instance, teacher_list,
                                                                   self.subjects_instance)
            top_doggie, best_fitness = hall_of_fame(current_schedule_offspring, fitness)
            new_population = crossover(current_schedule_offspring, fitness)
            new_mutated_population = mutate(new_population, mutation_chance, population_size)
            current_offspring = copy.deepcopy(new_mutated_population)
            current_offspring[0] = top_doggie
            current_offspring[1] = top_doggie
            current_offspring = copy.deepcopy(current_offspring)
            top_doggie_fitness = absolute_fitness(top_doggie,
                                                  self.rooms_instance, teacher_list,
                                                  self.subjects_instance)
            counter -= 1
            gen = population_size - counter

        top_doggie_str = []
        for schedule in top_doggie:
            room = find_room(schedule.id_room, self.rooms_instance)
            lecturer = find_lecturer(schedule.id_lecturer, self.lecturers_instance)
            subject = find_subject(schedule.id_subject, self.subjects_instance)
            lecture_str = (
                    'Room: ' + str(room.id_room) + '; Lecturer: ' + str(lecturer.name)
                    + ' ' + str(lecturer.surname)
                    + '; Subject: ' + str(subject.name))
            top_doggie_str.append(lecture_str)

        monday_list, tuesday_list, wednesday_list, thursday_list, friday_list = prepare_lists_for_df(top_doggie_str)

        data = {
            'Monday': monday_list,
            'Tuesday': tuesday_list,
            'Wednesday': wednesday_list,
            'Thursday': thursday_list,
            'Friday': friday_list
        }

        df = pd.DataFrame(data, index=[1, 2, 3, 4, 5, 6, 7, 8])
        df.to_excel(r'C:\Users\sofja\Documents\data.xlsx', index=True, header=True)
        print(top_doggie_fitness)
