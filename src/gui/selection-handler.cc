#include <QHBoxLayout>
#include <QLabel>
#include <QVector3D>
#include <QAction>
#include <QDebug>

#include <gepetto/gui/bodytreewidget.hh>
#include <gepetto/gui/mainwindow.hh>
#include <gepetto/gui/selection-event.hh>
#include <gepetto/gui/windows-manager.hh>
#include "gepetto/gui/selection-handler.hh"

namespace gepetto {
  namespace gui {
    SelectionHandler::SelectionHandler(WindowsManagerPtr_t wsm, QWidget *parent)
      : QComboBox(parent),
	index_(-1),
	wsm_(wsm)
    {
      connect(this, SIGNAL(currentIndexChanged(int)), SLOT(changeMode(int)));
    }

    SelectionHandler::~SelectionHandler()
    {
    }

    SelectionMode* SelectionHandler::mode ()
    {
      assert(index_ >= 0 && index_ < (int)modes_.size());
      return modes_[index_];
    }

    void SelectionHandler::changeMode(int index)
    {
      BodyTreeWidget* bt = MainWindow::instance()->bodyTree();
      foreach(QString name, selected_) {
        wsm_->setHighlight(name.toStdString(), 0);
      }
      if (index_ != -1) {
        modes_[index_]->reset();
        disconnect(bt, SIGNAL(bodySelected(SelectionEvent*)),
                   modes_[index_], SLOT(onSelect(SelectionEvent*)));
        disconnect(modes_[index_], SIGNAL(selectedBodies(QStringList)),
                   this, SLOT(getBodies(QStringList)));
      }
      index_ = index;
      connect(bt, SIGNAL(bodySelected(SelectionEvent*)),
              modes_[index], SLOT(onSelect(SelectionEvent*)),
              Qt::QueuedConnection);
      connect(modes_[index], SIGNAL(selectedBodies(QStringList)),
              SLOT(getBodies(QStringList)));
    }

    void SelectionHandler::addMode(SelectionMode* mode)
    {
      modes_.push_back(mode);
      addItem(mode->getName());
    }

    void SelectionHandler::getBodies(QStringList selectedBodies)
    {
      selected_ = selectedBodies;
    }

    UniqueSelection::UniqueSelection(WindowsManagerPtr_t wsm)
      : SelectionMode(wsm)
    {
    }

    UniqueSelection::~UniqueSelection()
    {
    }

    void UniqueSelection::onSelect(SelectionEvent* event)
    {
      if (!event) return;
      if (currentSelected_ == event->nodeName()) return;
      if (currentSelected_ != "") wsm_->setHighlight(currentSelected_.toStdString(), 0);
      currentSelected_ = event->nodeName();
      wsm_->setHighlight(event->node()->getID(), 8);
      emit selectedBodies(QStringList() << currentSelected_);
      event->done();
    }

    MultiSelection::MultiSelection(WindowsManagerPtr_t wsm)
      : SelectionMode(wsm)
    {
    }

    MultiSelection::~MultiSelection()
    {
    }

    void MultiSelection::reset()
    {
      SelectionMode::reset();
      selectedBodies_ = QStringList();
    }

    void MultiSelection::onSelect(SelectionEvent* event)
    {
      if (!event) return;
      int i = selectedBodies_.indexOf(event->nodeName());
      if (event->modKey() != Qt::ControlModifier) { // CTRL not pressed
        foreach (QString n, selectedBodies_) {
          wsm_->setHighlight(n.toStdString(), 0);
        }
        selectedBodies_.clear();
        currentSelected_ = event->nodeName();
        if (event->node()) {
          wsm_->setHighlight(event->node()->getID(), 8);
          selectedBodies_ << currentSelected_;
        }
      } else {                                    // CTRL pressed
        if (!currentSelected_.isEmpty())
          wsm_->setHighlight(currentSelected_.toStdString(), 7);
        if (i >= 0) {                             // Already selected.
          wsm_->setHighlight(event->node()->getID(), 0);
          currentSelected_ = "";
          selectedBodies_.removeAt(i);
        } else {
          currentSelected_ = event->nodeName();
          if (event->node()){   // Add to the list if not empty
            wsm_->setHighlight(event->node()->getID(), 8);
            selectedBodies_ << currentSelected_;
          }
        }
      }
      qDebug() << selectedBodies_;
      emit selectedBodies(selectedBodies_);
      event->done();
    }
  }
}
