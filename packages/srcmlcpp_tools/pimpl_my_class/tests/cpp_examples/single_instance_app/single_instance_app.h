#pragma once
#include <string>
#include <memory>

class SingleInstanceAppPImpl;

class SingleInstanceApp
{
public:
    //
    //  SingleInstanceApp enables to make sure that only one instance of an app runs on a given system
    //
    // Construct a Single Instance
    SingleInstanceApp(const std::string & lockName);
    // RunSingleInstanceListener will run an async loop
    // that will wait for signals from possible other instances launches
    // If a signal is received:
    // - It will tell the other instance that an instance is launched already
    //   (i.e for the other instance, RunSingleInstanceListener() will return false)
    // - It will store a "ping" in the main instance
    //   (so that in the main loop, one can for example bring the main instance app to the front)
    bool RunSingleInstanceListener();// Will return false if another instance was detected!
    // Returns true if a ping was received from another instance
    bool WasPinged() const;// Blah
    ~SingleInstanceApp();
private:
    std::unique_ptr<SingleInstanceAppPImpl> mPImpl;
};