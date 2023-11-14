/**
 * @brief Prints a greeting message to the console.
 *
 * This function demonstrates basic output to the console using std::cout. It can be
 * expanded to include more complex functionality or more detailed messages.
 * 
 * @param message The greeting message to be printed.
 */
void printGreeting(const std::string& message) {
    std::cout << message << std::endl;
}

/**
 * @brief Main entry point of the program.
 * 
 * This main function calls printGreeting to demonstrate basic output functionality.
 * 
 * @return int Returns 0 to indicate successful execution.
 */
int main() {
    printGreeting("Hello Security World!");
    return 0;
}