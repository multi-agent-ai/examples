// Use something like this to compile:
// g++ example_02.cpp -o example_02  -std=c++11 -O3

#include <iostream>
#include <sstream>
#include <cstdlib>
#include <chrono>
#include <thread>
#include <cmath>
#include <algorithm>
#include <random>
#include <list>
#include <fstream>
#include <time.h>

const double WORLD_WIDTH = 2560.0;
const double WORLD_HEIGHT = 1440.0;

class Agent {
public:
    double vmax = 0.0;
    double x;
    double y;
    double dx = 0.0;
    double dy = 0.0;
    bool is_alive = true;
    Agent* target = NULL;
    int age = 0;
    int energy = 0;

    Agent() {
        x = WORLD_WIDTH * (rand() / (RAND_MAX + 1.0));
        y = WORLD_HEIGHT * (rand() / (RAND_MAX + 1.0));
    }

    void update(const std::vector<Agent*>& food) {
        age++;

        // we can't move
        if (vmax == 0.0) { return; }

        // target is dead, don't chase it further
        if ((target != NULL) && (target->is_alive == false)) {
            target = NULL;
        }
    
        // periodically loose target
        if ((target != NULL) && ((double) rand() / (RAND_MAX)) < 0.1) {
            target = NULL;
        }

        // eat the target if close enough
        if (target != NULL) {
            double squared_dist = pow((x - target->x), 2) + pow((y - target->y), 2);
            if (squared_dist < 400) {
                target->is_alive = false;
                energy++;
            }
        }

        // agent doesn't have a target, find a new one
        if (target == NULL) {
            double min_dist = 9999999;
            Agent* min_agent = NULL;

            for (const auto a: food) {
                if (a->is_alive == true) {
                    double squared_dist = pow((x - a->x), 2) + pow((y - a->y), 2);
                    if (squared_dist < min_dist) {
                        min_dist = squared_dist;
                        min_agent = a;
                    }
                }
            }
            if (min_dist < 100000) {
                target = min_agent;
            }
        }

        // initialize forces to zero
        double fx = 0;
        double fy = 0;

        // move in the direction of the target, if any
        if (target != NULL) {
            fx += 0.1*(target->x - x);
            fy += 0.1*(target->y - y);
        }

        // update our direction based on the 'force'
        dx += 0.05 * fx;
        dy += 0.05 * fy;

        // slow down agent if it moves faster than its max velocity
        double velocity = sqrt(pow(dx, 2) + pow(dy, 2));
        if (velocity > vmax) {
            dx = (dx / velocity) * (vmax);
            dy = (dy / velocity) * (vmax);
        }

        // update position based on delta x/y
        x += dx;
        y += dy;

        // ensure it stays within the world boundaries
        x = std::max(x, 0.0);
        x = std::min(x, WORLD_WIDTH);
        y = std::max(y, 0.0);
        y = std::min(y, WORLD_HEIGHT);
    }
};


class Predator: public Agent {
    public:
    Predator() : Agent() {
         vmax = 2.5;
    }
};

class Prey: public Agent {
    public:
    Prey() : Agent() {
         vmax = 2.0;
    }
};

class Plant: public Agent {
    public:
    Plant() : Agent() {
         vmax = 0.0;
    }
};

int main(int argc, char *argv[]) {
    srand (time(NULL));

    std::ios_base::sync_with_stdio(false);

    std::vector<Agent*> predators;
    std::vector<Agent*> preys;
    std::vector<Agent*> plants;

    // create initial agents
    for (int i = 0; i < 10; i++) {
        Predator *p = new Predator();
        predators.push_back(p);
    }
    for (int i = 0; i < 10; i++) {
        Prey *p = new Prey();
        preys.push_back(p);
    }
    for (int i = 0; i < 100; i++) {
        Plant *p = new Plant();
        plants.push_back(p);
    }

    std::ofstream outfile;
    outfile.open ("output.csv");

    int timestep = 0;
    outfile << timestep << ',' << "Title" << ',' << "Predator Prey Relationship / Example 02 / C++" << std::endl;

    while (timestep < 10000) {

        // update all agents
        for (auto p: predators) { p->update(preys); }
        for (auto p: preys) { p->update(plants); }

        // handle eaten and create new plants
        plants.erase(
            std::remove_if(
                plants.begin(), 
                plants.end(),
                [](const Agent* a)
                {return !a->is_alive;}),
            plants.end());
        
        for (int i=0; i < 2; i++) { plants.push_back(new Plant()); };
        
        // handle eaten and create new preys
        preys.erase(
            std::remove_if(
                preys.begin(), 
                preys.end(),
                [](const Agent* a)
                {return !a->is_alive;}),
            preys.end());
        
        std::vector<Agent*>::size_type preys_size = preys.size();
        for (std::vector<Agent*>::size_type i = 0; i < preys_size; ++i) {
            if (preys[i]->energy > 10) {
                preys[i]->energy = 0;
                Prey* np = new Prey();
                np->x = preys[i]->x + -20 + 40 * (rand() / (RAND_MAX + 1.0));
                np->y = preys[i]->y + -20 + 40 * (rand() / (RAND_MAX + 1.0));
                preys.push_back(np);
            }
        }

        // handle old and create new predators
        predators.erase(
            std::remove_if(
                predators.begin(), 
                predators.end(),
                [](const Agent* a)
                {return a->age > 2000;}),
            predators.end());

        std::vector<Agent*>::size_type predators_size = predators.size();
        for (std::vector<Agent*>::size_type i = 0; i < predators_size; ++i) {
            if (predators[i]->energy > 10) {
                predators[i]->energy = 0;
                Predator* np = new Predator();
                np->x = predators[i]->x + -20 + 40 * (rand() / (RAND_MAX + 1.0));
                np->y = predators[i]->y + -20 + 40 * (rand() / (RAND_MAX + 1.0));
                predators.push_back(np);
            }
        }

        // write data to output file
        /*
        for (const auto p: predators) {
            outfile << timestep << ',' << "Position" << ',' << "Predator" << ',' << p->x << ',' << p->y << '\n';
        }

        for (const auto p: preys) {
            outfile << timestep << ',' << "Position" << ',' << "Prey" << ',' << p->x << ',' << p->y << '\n';
        }
        
        for (const auto p: plants) {
            outfile << timestep << ',' << "Position" << ',' << "Plant" << ',' << p->x << ',' << p->y << '\n';
        }
        */
        timestep++;
    }

    outfile.close();
    std::cout << "ok " << predators.size() << ", " << preys.size() << ", " << plants.size() << std::endl;
}
