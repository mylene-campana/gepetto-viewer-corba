#ifndef GEPETTO_GUI_SETTINGS_HH
#define GEPETTO_GUI_SETTINGS_HH

#include <ostream>
#include <string>
#include <QString>
#include <QStringList>

#include <gepetto/gui/dialog/pluginmanagerdialog.hh>

namespace gepetto {
  namespace gui {
    class MainWindow;

    /// Settings manager for the interface.
    ///
    /// This struct is responsible for parsing configuration files as follow:
    /// - Robots file: Settings::readRobotFile()
    /// - Environments file: Settings::readEnvFile()
    /// - Configuration file: Settings::readSettingFile()
    struct Settings {
      std::string configurationFile;
      std::string predifinedRobotConf;
      std::string predifinedEnvConf;

      bool verbose;
      bool noPlugin;
      bool autoWriteSettings;
      bool startGepettoCorbaServer;

      int refreshRate;

      std::string captureDirectory, captureFilename, captureExtension;

      QString installDirectory;

      /// Set up default values
      Settings (const char* installDirectory);

      /// Setup paths to find setting files and plugins.
      /// \note The environment variable
      /// GEPETTO_GUI_PLUGIN_DIRS, LD_LIBRARY_PATH
      /// and GEPETTO_GUI_SETTINGS_DIR are read.
      void setupPaths () const;

      /// Update values accordingly with command arguments
      int fromArgv (const int argc, char* const argv[]);

      /// Update settings from setting files
      void fromFiles ();

      /// Write the settings to configuration files
      void writeSettings ();

      /// Get a setting
      QVariant getSetting (const QString & key,
          const QVariant & defaultValue = QVariant());

      PluginManager pluginManager_;
      QStringList pluginsToInit_;
      QStringList pyplugins_;

      void setMainWindow (MainWindow* main);

      void initPlugins ();

      std::ostream& print (std::ostream& os);

      /// \note Prefer using Settings::fromFiles()
      void readRobotFile ();
      /// \note Prefer using Settings::fromFiles()
      void readEnvFile ();
      /// Read the settings file.
      ///
      /// Here is the syntax:
      /// \code
      /// ; Comments starts with a ; You may uncomment to see the effect.
      ///
      /// [plugins]
      /// ; Put a list of C++ plugins followed by '=true'. For instance, HPP users may have
      /// ; libhppwidgetsplugin.so=true
      /// ; libhppcorbaserverplugin.so=true
      ///
      /// [pyplugins]
      /// ; Put a list of Python plugins followed by '=true'. For instance, the example plugin can be loaded with
      /// ; gepetto.plugin=true
      ///
      /// ; WARNING: Any comment in this file may be removed by the GUI if you regenerate a configuration file.
      /// \endcode
      /// \note Details on plugin interface can be found in PluginInterface, resp. PythonWidget, class
      /// for C++, resp. Python, plugins.
      /// \note Prefer using Settings::fromFiles()
      void readSettingFile ();

    private:
      void writeRobotFile ();
      void writeEnvFile ();
      void writeSettingFile ();

      void addRobotFromString (const std::string& rbtStr);
      void addEnvFromString (const std::string& envStr);
      void addPlugin (const QString& plg, bool init);
      void addPyPlugin (const QString& plg, bool init);

      inline void log (const QString& t);
      inline void logError (const QString& t);

      MainWindow* mw;
    };
  } // namespace gui
} // namespace gepetto

#endif // GEPETTO_GUI_SETTINGS_HH
