// /**
//  * @brief Prints a greeting message to the console.
//  *
//  * This function demonstrates basic output to the console using std::cout. It can be
//  * expanded to include more complex functionality or more detailed messages.
//  * 
//  * @param message The greeting message to be printed.
//  */
// void printGreeting(const std::string& message) {
//     std::cout << message << std::endl;
// }

// /**
//  * @brief Main entry point of the program.
//  * 
//  * This main function calls printGreeting to demonstrate basic output functionality.
//  * 
//  * @return int Returns 0 to indicate successful execution.
//  */
// int main() {
//     printGreeting("Hello Security World!");
//     return 0;
// }
#include <QApplication>
#include <QMainWindow>
#include "adapters/gui/qt-ui-components/ui_textinterface.h"  // Include the generated header file

/**
 * @brief Main program
 * 
 * Runs a simple UI component for Qt testing purposes
 *
 * @param argc 
 * @param argv 
 * @return int 
 */
int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    QMainWindow window;

    Ui::Form ui;  // Use the generated UI class
    ui.setupUi(&window);

    window.show();
    return app.exec();
}